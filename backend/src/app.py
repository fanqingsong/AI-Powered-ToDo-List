from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import AsyncExitStack
from dotenv import load_dotenv
from .services import TaskService
from .agents import TaskAgent
from .routes import create_api_routes

# Load environment variables from .env file
load_dotenv()


class TaskManagerApp:
    """FastAPI application for task management with AI agents."""
    
    def __init__(self):
        # Auto-detect server URL: Azure App Service or local development
        if os.getenv("WEBSITE_HOSTNAME"):
            # Running in Azure App Service
            server_url = f"https://{os.getenv('WEBSITE_HOSTNAME')}"
        else:
            # Local development
            server_url = "http://localhost:3000"
        
        self.app = FastAPI(
            title="Task Manager API",
            version="1.0.0",
            description="A simple task management API with LangGraph AI Agents",
            servers=[
                {"url": server_url, "description": "Task Manager API Server"}
            ]
        )

        # Legacy variables removed - now using LangGraph agent

        # Initialize services
        self.task_service = TaskService()
        self.task_agent = TaskAgent(self.task_service)
        
        self._setup_middleware()


        @self.app.on_event("startup")
        async def startup_event():
            self._setup_routes()  

        @self.app.on_event("shutdown")
        async def shutdown_event():
            """Cleanup resources."""
            print("Shutting down Task Manager app...")
            self.task_service.close()
            await self.task_agent.cleanup()
    
    def _setup_middleware(self):
        """Set up CORS and other middleware."""
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],  # Configure as needed for production
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
      
    def _setup_routes(self):
        """Set up API routes."""
        # API routes
        api_router = create_api_routes(
            self.task_service,
            self.task_agent
        )
        self.app.include_router(api_router, prefix="/api")
        
        # Root endpoint
        @self.app.get("/")
        async def root():
            return {
                "message": "Task Manager API",
                "version": "1.0.0",
                "docs": "/docs",
                "frontend": "Please run the React frontend separately"
            }
    
    def get_app(self) -> FastAPI:
        """Get the FastAPI application instance."""
        return self.app
    


# Create the application instance
app_instance = TaskManagerApp()
app = app_instance.get_app()


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", "3000"))
    uvicorn.run(
        "src.app:app",
        host="0.0.0.0",
        port=port,
        reload=True
    )
