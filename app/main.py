from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pathlib import Path
import os

from app.database import init_db
from app.config import settings

# Import API routers
from app.routes import users, appointments, chatbot, reports, period, health_tips, doctors, medical_records

# Import page routes
from app.routes.pages import router as pages_router

# Initialize database
init_db()

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="Healthcare Web Application API",
    version="1.0.0"
)

# CORS middleware - allow frontend to access API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the base directory
BASE_DIR = Path(__file__).resolve().parent

# Mount static files directory
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# Mount uploads directory for file access
uploads_dir = BASE_DIR / "uploads"
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory=str(uploads_dir)), name="uploads")

# Setup Jinja2 templates
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

# Include API routers with /api prefix
app.include_router(users.router, prefix="/api")
app.include_router(appointments.router, prefix="/api")
app.include_router(chatbot.router, prefix="/api")
app.include_router(reports.router, prefix="/api")
app.include_router(period.router, prefix="/api")
app.include_router(health_tips.router, prefix="/api")
app.include_router(doctors.router, prefix="/api")
app.include_router(medical_records.router, prefix="/api")

# Include page routes (HTML pages)
app.include_router(pages_router)

# Health check endpoint
@app.get("/api/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
