from typing import List

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.auth.middleware import get_current_user
from app.config import get_settings
from app.database.database import get_db
from app.database.models import AgentConfig
from app.agents.manager import init_agent_manager

router = APIRouter(prefix="/api/admin", tags=["Admin"])


class AgentResponse(BaseModel):
    id: int
    name: str
    description: str | None
    system_prompt: str
    model: str | None
    db_uri: str | None
    schema_name: str | None
    is_active: bool
    tool_names: str | None

    class Config:
        orm_mode = True


class AgentUpdateRequest(BaseModel):
    description: str | None = None
    system_prompt: str | None = None
    model: str | None = None
    db_uri: str | None = None
    schema_name: str | None = None
    is_active: bool | None = None
    tool_names: str | None = None


@router.get("/agents", response_model=List[AgentResponse])
def list_agents(user_id: int = Depends(get_current_user), db: Session = Depends(get_db)):
    agents = (
        db.query(AgentConfig)
        .order_by(AgentConfig.name.asc())
        .all()
    )
    return agents


@router.put("/agents/{agent_id}", response_model=AgentResponse)
def update_agent(
    agent_id: int,
    payload: AgentUpdateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    agent = db.query(AgentConfig).filter(AgentConfig.id == agent_id).first()
    if not agent:
        raise HTTPException(status_code=404, detail="Agente non trovato.")

    if payload.description is not None:
        agent.description = payload.description
    if payload.system_prompt is not None:
        agent.system_prompt = payload.system_prompt
    if payload.model is not None:
        agent.model = payload.model
    if payload.db_uri is not None:
        agent.db_uri = payload.db_uri
    if payload.schema_name is not None:
        agent.schema_name = payload.schema_name
    if payload.is_active is not None:
        agent.is_active = payload.is_active
    if payload.tool_names is not None:
        agent.tool_names = payload.tool_names

    db.add(agent)
    db.commit()
    db.refresh(agent)

    # Reinitialize AgentManager so changes take effect immediately
    settings = get_settings()
    init_agent_manager(settings)

    return agent


# ========================================
# SCHEDULED TASKS ENDPOINTS
# ========================================

from datetime import datetime
from app.database.models import ScheduledTask
from app.services.scheduler_service import get_scheduler_service
from app.services.email_service import EmailService
from app.agents.manager import get_agent_manager
import json
import logging

logger = logging.getLogger(__name__)


class ScheduleCreateRequest(BaseModel):
    name: str
    description: str | None = None
    agent_name: str
    prompt: str
    cron_expression: str
    recipient_emails: List[str]
    is_active: bool = True


class ScheduleUpdateRequest(BaseModel):
    name: str | None = None
    description: str | None = None
    agent_name: str | None = None
    prompt: str | None = None
    cron_expression: str | None = None
    recipient_emails: List[str] | None = None
    is_active: bool | None = None


class ScheduleResponse(BaseModel):
    id: int
    name: str
    description: str | None
    agent_name: str
    prompt: str
    cron_expression: str
    recipient_emails: List[str]
    is_active: bool
    last_run_at: datetime | None
    next_run_at: datetime | None
    last_run_status: str | None
    last_run_error: str | None
    created_by_user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True

    @classmethod
    def from_orm(cls, obj: ScheduledTask):
        data = {
            "id": obj.id,
            "name": obj.name,
            "description": obj.description,
            "agent_name": obj.agent_name,
            "prompt": obj.prompt,
            "cron_expression": obj.cron_expression,
            "recipient_emails": json.loads(obj.recipient_emails) if obj.recipient_emails else [],
            "is_active": obj.is_active,
            "last_run_at": obj.last_run_at,
            "next_run_at": obj.next_run_at,
            "last_run_status": obj.last_run_status,
            "last_run_error": obj.last_run_error,
            "created_by_user_id": obj.created_by_user_id,
            "created_at": obj.created_at,
            "updated_at": obj.updated_at,
        }
        return cls(**data)


async def execute_scheduled_task(task_id: int, db: Session):
    """
    Execute a scheduled task: run agent query and send email report.
    This is called by the scheduler.
    """
    task = db.query(ScheduledTask).filter(ScheduledTask.id == task_id).first()
    if not task or not task.is_active:
        logger.warning(f"Scheduled task {task_id} not found or inactive, skipping")
        return

    logger.info(f"Executing scheduled task: {task.name} (ID: {task_id})")

    # Update status to pending
    task.last_run_at = datetime.now()
    task.last_run_status = "pending"
    task.last_run_error = None
    db.commit()

    try:
        # Get agent manager and execute query
        agent_manager = get_agent_manager()
        agent = agent_manager.get_agent(task.agent_name)

        if not agent:
            raise ValueError(f"Agent '{task.agent_name}' not found")

        # Execute agent query using datapizza-ai Agent API
        # Use a_run() instead of ainvoke() - it's the correct async method
        result = await agent.a_run(task.prompt)

        # Extract response content
        if hasattr(result, "text") and getattr(result, "text", None):
            response_text = result.text
        elif isinstance(result, str):
            response_text = result
        else:
            response_text = str(result) if result is not None else ""

        # Send email report
        settings = get_settings()
        email_service = EmailService(
            smtp_host=settings.smtp_host,
            smtp_port=settings.smtp_port,
            smtp_username=settings.smtp_username,
            smtp_password=settings.smtp_password,
            smtp_use_ssl=settings.smtp_use_ssl,
            from_email=settings.smtp_from_email,
        )

        # Format email
        subject = f"Report Automatico: {task.name} - {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        body_html = email_service.format_report_html(
            task_name=task.name,
            prompt=task.prompt,
            agent_name=task.agent_name,
            response=response_text,
            execution_time=datetime.now().strftime("%d/%m/%Y %H:%M:%S"),
        )

        # Parse recipients
        recipients = json.loads(task.recipient_emails) if isinstance(task.recipient_emails, str) else task.recipient_emails

        # Send email
        success = email_service.send_report_email(
            subject=subject,
            body_html=body_html,
            recipients=recipients,
            task_name=task.name,
        )

        if success:
            task.last_run_status = "success"
            logger.info(f"Scheduled task {task.name} completed successfully")
        else:
            task.last_run_status = "failed"
            task.last_run_error = "Failed to send email"
            logger.error(f"Scheduled task {task.name} failed to send email")

    except Exception as e:
        task.last_run_status = "failed"
        task.last_run_error = str(e)
        logger.error(f"Scheduled task {task.name} failed: {str(e)}")

    finally:
        # Update next run time from scheduler
        scheduler = get_scheduler_service()
        task.next_run_at = scheduler.get_next_run_time(str(task.id))
        db.commit()


@router.get("/schedules", response_model=List[ScheduleResponse])
def list_schedules(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Get all scheduled tasks."""
    tasks = db.query(ScheduledTask).order_by(ScheduledTask.created_at.desc()).all()
    
    # Update next_run_at from scheduler for active tasks
    scheduler = get_scheduler_service()
    for task in tasks:
        if task.is_active:
            task.next_run_at = scheduler.get_next_run_time(str(task.id))
    
    return [ScheduleResponse.from_orm(task) for task in tasks]


@router.post("/schedules", response_model=ScheduleResponse)
def create_schedule(
    payload: ScheduleCreateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Create a new scheduled task."""
    # Validate agent exists
    agent_manager = get_agent_manager()
    if not agent_manager.get_agent(payload.agent_name):
        raise HTTPException(status_code=400, detail=f"Agent '{payload.agent_name}' not found")

    # Create task
    task = ScheduledTask(
        name=payload.name,
        description=payload.description,
        agent_name=payload.agent_name,
        prompt=payload.prompt,
        cron_expression=payload.cron_expression,
        recipient_emails=json.dumps(payload.recipient_emails),
        is_active=payload.is_active,
        created_by_user_id=user_id,
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    # Schedule task if active
    if task.is_active:
        scheduler = get_scheduler_service()
        from functools import partial
        
        # Create callback with db session factory
        from app.database.database import SessionLocal
        def task_callback(task_id: int):
            import asyncio
            db_session = SessionLocal()
            try:
                asyncio.run(execute_scheduled_task(task_id, db_session))
            finally:
                db_session.close()
        
        scheduler.add_task(
            task_id=str(task.id),
            cron_expression=task.cron_expression,
            callback=task_callback,
            task_name=task.name,
        )
        task.next_run_at = scheduler.get_next_run_time(str(task.id))
        db.commit()

    return ScheduleResponse.from_orm(task)


@router.put("/schedules/{schedule_id}", response_model=ScheduleResponse)
def update_schedule(
    schedule_id: int,
    payload: ScheduleUpdateRequest,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Update a scheduled task."""
    task = db.query(ScheduledTask).filter(ScheduledTask.id == schedule_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")

    # Update fields
    if payload.name is not None:
        task.name = payload.name
    if payload.description is not None:
        task.description = payload.description
    if payload.agent_name is not None:
        # Validate agent exists
        agent_manager = get_agent_manager()
        if not agent_manager.get_agent(payload.agent_name):
            raise HTTPException(status_code=400, detail=f"Agent '{payload.agent_name}' not found")
        task.agent_name = payload.agent_name
    if payload.prompt is not None:
        task.prompt = payload.prompt
    if payload.cron_expression is not None:
        task.cron_expression = payload.cron_expression
    if payload.recipient_emails is not None:
        task.recipient_emails = json.dumps(payload.recipient_emails)
    if payload.is_active is not None:
        task.is_active = payload.is_active

    db.commit()
    db.refresh(task)

    # Update scheduler
    scheduler = get_scheduler_service()
    if task.is_active:
        from app.database.database import SessionLocal
        def task_callback(task_id: int):
            import asyncio
            db_session = SessionLocal()
            try:
                asyncio.run(execute_scheduled_task(task_id, db_session))
            finally:
                db_session.close()
        
        scheduler.add_task(
            task_id=str(task.id),
            cron_expression=task.cron_expression,
            callback=task_callback,
            task_name=task.name,
        )
        task.next_run_at = scheduler.get_next_run_time(str(task.id))
    else:
        scheduler.remove_task(str(task.id))
        task.next_run_at = None

    db.commit()
    return ScheduleResponse.from_orm(task)


@router.delete("/schedules/{schedule_id}")
def delete_schedule(
    schedule_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Delete a scheduled task."""
    task = db.query(ScheduledTask).filter(ScheduledTask.id == schedule_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")

    # Remove from scheduler
    scheduler = get_scheduler_service()
    scheduler.remove_task(str(task.id))

    # Delete from database
    db.delete(task)
    db.commit()

    return {"message": "Scheduled task deleted successfully"}


@router.post("/schedules/{schedule_id}/test")
async def test_schedule(
    schedule_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Manually execute a scheduled task for testing."""
    task = db.query(ScheduledTask).filter(ScheduledTask.id == schedule_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Scheduled task not found")

    # Execute task
    await execute_scheduled_task(schedule_id, db)

    # Refresh to get updated status
    db.refresh(task)

    return {
        "message": "Test execution completed",
        "status": task.last_run_status,
        "error": task.last_run_error,
    }

