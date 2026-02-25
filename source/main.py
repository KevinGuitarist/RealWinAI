import asyncio
from typing import List
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import HTMLResponse, RedirectResponse
from source.app.users.utils import create_admin
from source.core.database import database_health, get_db
from source.core.routers import api_router
from source.core.schemas import HealthSchema
from source.core.settings import settings
# Billing scheduler disabled - subscriptions not enforced
# from source.app.subscriptions.billing import start_scheduler, scheduler
from source.app.MAX.integration import setup_max_webhooks, max_lifespan


app = FastAPI(
    title=settings.APP_TITLE,
    version=settings.VERSION,
    docs_url="/docs",
    redoc_url=None,
    openapi_url="/openapi.json",
    lifespan=max_lifespan
)


app.include_router(api_router)

# Setup M.A.X. Webhook System
setup_max_webhooks(app)

# Mount static files for frontend
import os
static_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static")
frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")

# Serve static assets
if os.path.exists(static_path):
    app.mount("/static", StaticFiles(directory=static_path), name="static")

# Serve frontend build - mount API routes first, then frontend as catch-all
if os.path.exists(frontend_path):
    @app.get("/{full_path:path}", include_in_schema=False)
    async def serve_frontend(full_path: str):
        """Serve frontend for non-API routes"""
        from fastapi.responses import FileResponse
        import os
        
        # If path starts with 'api', let FastAPI handle it
        if full_path.startswith('api/') or full_path.startswith('docs') or full_path.startswith('health'):
            return None
            
        file_path = os.path.join(frontend_path, full_path)
        
        # If file exists, serve it
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        
        # Otherwise serve index.html for SPA routing
        index_path = os.path.join(frontend_path, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        
        return {"error": "Frontend not found"}
else:
    print("⚠️ Frontend build not found at:", frontend_path)

origins = [
    "https://realwin-frontend-master.vercel.app",  # Production frontend
    "https://realwin-frontend-master-a7tonaavf-vaibhav05-edus-projects.vercel.app",  # Vercel preview URL
    "https://realwinai.onrender.com",  # Render deployment
    "http://localhost:3000",  # For local development
    "http://localhost:5173",  # For Vite dev server
    "http://localhost:8080",  # For Vite dev server (configured port)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["*"]
)


# Billing scheduler disabled - subscriptions not enforced
# @app.on_event("startup")
# async def _start_billing():
#     start_scheduler()


# @app.on_event("shutdown")
# async def _stop_billing():
#     try:
#         scheduler.shutdown(wait=False)
#     except Exception:
#         pass


@app.get("/", tags=["Health"], include_in_schema=False)
async def root():
    """Serve frontend root"""
    from fastapi.responses import FileResponse
    import os
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend", "dist")
    index_path = os.path.join(frontend_path, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"message": "RealWin.AI Backend API", "docs": "/docs"}


@app.get("/health", response_model=HealthSchema, tags=["Health"])
async def health_check(db: AsyncSession = Depends(get_db)):
    return {"api": True, "database": await database_health(db=db)}


@app.get("/chat", response_class=HTMLResponse, include_in_schema=False)
async def chat_interface():
    """Serve the M.A.X. chat interface"""
    import os
    chat_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), "static", "chat.html")
    if os.path.exists(chat_file):
        with open(chat_file, "r") as f:
            return HTMLResponse(content=f.read())
    return HTMLResponse(content="<h1>Chat interface not found</h1>", status_code=404)
