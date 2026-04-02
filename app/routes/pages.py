from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates
from pathlib import Path

router = APIRouter(tags=["pages"])

# Setup templates
BASE_DIR = Path(__file__).resolve().parent.parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@router.get("/")
async def login_page(request: Request):
    """Login page (index.html)"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/login")
async def login_redirect(request: Request):
    """Login page redirect"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/register")
async def register_page(request: Request):
    """Registration page"""
    return templates.TemplateResponse("register.html", {"request": request})


@router.get("/dashboard")
async def dashboard_page(request: Request):
    """Patient dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@router.get("/chatbot")
async def chatbot_page(request: Request):
    """Chatbot page"""
    return templates.TemplateResponse("chatbot.html", {"request": request})


@router.get("/appointments")
async def appointments_page(request: Request):
    """Appointments page"""
    return templates.TemplateResponse("appointment.html", {"request": request})


@router.get("/doctors")
async def doctors_page(request: Request):
    """Find doctors page"""
    return templates.TemplateResponse("doctors.html", {"request": request})


@router.get("/doctor-dashboard")
async def doctor_dashboard_page(request: Request):
    """Doctor dashboard page"""
    return templates.TemplateResponse("doctor_dashboard.html", {"request": request})


@router.get("/period")
async def period_tracker_page(request: Request):
    """Period tracker page"""
    return templates.TemplateResponse("period.html", {"request": request})


@router.get("/reports")
async def reports_page(request: Request):
    """Medical reports page"""
    return templates.TemplateResponse("upload.html", {"request": request})


@router.get("/upload")
async def upload_page(request: Request):
    """Upload reports page (alias)"""
    return templates.TemplateResponse("upload.html", {"request": request})
