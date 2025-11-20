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
