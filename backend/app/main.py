"""
FastAPI application entry point.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.config import get_settings
from app.agents.manager import init_agent_manager
from app.auth.routes import router as auth_router
from app.chat.routes import router as chat_router
from app.admin.routes import router as admin_router

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for startup and shutdown events.
    """
    # Startup: Initialize agent manager
    print("Initializing agent manager...")
    init_agent_manager(settings)
    print("Agent manager initialized successfully.")
    
    # Startup: Initialize and start scheduler
    print("Initializing scheduler service...")
    from app.services.scheduler_service import get_scheduler_service
    from app.database.database import SessionLocal
    from app.database.models import ScheduledTask
    from app.admin.routes import execute_scheduled_task
    import asyncio
    
    scheduler = get_scheduler_service()
    scheduler.start()
    
    # Load active scheduled tasks from database
    db = SessionLocal()
    try:
        active_tasks = db.query(ScheduledTask).filter(ScheduledTask.is_active == True).all()
        print(f"Loading {len(active_tasks)} active scheduled task(s)...")
        
        for task in active_tasks:
            def task_callback(task_id: int):
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
            print(f"  - Loaded task: {task.name} (cron: {task.cron_expression})")
        
        print("Scheduler service started successfully.")
    finally:
        db.close()
    
    yield
    
    # Shutdown: Stop scheduler and cleanup
    print("Shutting down scheduler...")
    scheduler.shutdown()
    print("Shutting down application...")


# Create FastAPI app
app = FastAPI(
    title="Multi-Agent Chat System",
    description="Sistema di chat multi-agente per interrogare database SQL Server",
    version="1.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:8501"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(auth_router)
app.include_router(chat_router)
app.include_router(admin_router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Multi-Agent Chat System API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "multi-agent-chat"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
