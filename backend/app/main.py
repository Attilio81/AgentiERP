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
    
    yield
    
    # Shutdown: Cleanup if needed
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
