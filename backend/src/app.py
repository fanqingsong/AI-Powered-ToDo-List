from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from contextlib import AsyncExitStack, asynccontextmanager
from dotenv import load_dotenv
from .services import TaskService, ConversationService
from .services.admin_init_service import admin_init_service
from .agents import TaskAgent
from .routes import create_api_routes
from .routes.auth import create_auth_routes
from .routes.admin import create_admin_routes
from .routes.schedule import create_schedule_routes
from .routes.note import create_note_routes
from .routes.analytics import create_analytics_routes
from .routes.smart_search import router as smart_search_router

# Load environment variables from .env file
load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    # 启动时执行
    print("🚀 正在启动 AI Native 智能工作台...")
    
    # 初始化数据库架构和管理员账户
    print("📊 正在初始化数据库架构...")
    schema_ok = await admin_init_service.initialize_database_schema()
    
    if schema_ok:
        print("👤 正在检查管理员账户...")
        admin_ok = await admin_init_service.ensure_admin_exists()
        
        if admin_ok:
            print("✅ 管理员账户检查完成")
        else:
            print("⚠️ 管理员账户初始化失败，但应用将继续启动")
    else:
        print("❌ 数据库架构初始化失败")
    
    print("🎉 AI Native 智能工作台启动完成！")
    
    yield
    
    # 关闭时执行
    print("Shutting down Task Manager app...")


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
            ],
            lifespan=lifespan
        )

        # Initialize services
        self.task_service = TaskService()
        self.conversation_service = ConversationService()
        self.task_agent = TaskAgent(self.task_service)
        
        self._setup_middleware()
        self._setup_routes()
    
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
        try:
            # API routes
            print("Creating API routes...")
            api_router = create_api_routes(
                self.task_service,
                self.task_agent,
                self.conversation_service
            )
            self.app.include_router(api_router, prefix="/api")
            print("API routes registered successfully")
            
            # Auth routes
            print("Creating auth routes...")
            auth_router = create_auth_routes()
            self.app.include_router(auth_router, prefix="/api/auth")
            print("Auth routes registered successfully")
            
            # Admin routes
            print("Creating admin routes...")
            try:
                admin_router = create_admin_routes()
                self.app.include_router(admin_router, prefix="/api/admin")
                print("Admin routes registered successfully")
            except Exception as e:
                print(f"Error creating admin routes: {e}")
                import traceback
                traceback.print_exc()
            
            # Schedule routes
            print("Creating schedule routes...")
            try:
                schedule_router = create_schedule_routes()
                self.app.include_router(schedule_router, prefix="/api/schedules")
                print("Schedule routes registered successfully")
            except Exception as e:
                print(f"Error creating schedule routes: {e}")
                import traceback
                traceback.print_exc()
            
            # Note routes
            print("Creating note routes...")
            try:
                note_router = create_note_routes()
                self.app.include_router(note_router, prefix="/api/notes")
                print("Note routes registered successfully")
            except Exception as e:
                print(f"Error creating note routes: {e}")
                import traceback
                traceback.print_exc()
            
            # Analytics routes
            print("Creating analytics routes...")
            try:
                analytics_router = create_analytics_routes()
                self.app.include_router(analytics_router, prefix="/api/analytics")
                print("Analytics routes registered successfully")
            except Exception as e:
                print(f"Error creating analytics routes: {e}")
                import traceback
                traceback.print_exc()
            
            # Smart search routes
            print("Creating smart search routes...")
            try:
                self.app.include_router(smart_search_router, prefix="/api/smart-search")
                print("Smart search routes registered successfully")
            except Exception as e:
                print(f"Error creating smart search routes: {e}")
                import traceback
                traceback.print_exc()
            
            # Root endpoint
            @self.app.get("/")
            async def root():
                return {
                    "message": "Task Manager API",
                    "version": "1.0.0",
                    "docs": "/docs",
                    "frontend": "Please run the React frontend separately"
                }
            print("Root endpoint registered successfully")
        except Exception as e:
            print(f"Error setting up routes: {e}")
            import traceback
            traceback.print_exc()
    
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
