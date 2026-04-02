from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

# User Models
class UserCreate(BaseModel):
    name: str = Field(..., min_length=1)
    email: EmailStr
    password: str = Field(..., min_length=6)
    age: Optional[int] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age: Optional[int] = None
    
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse

# Appointment Models
class AppointmentCreate(BaseModel):
    doctor_name: str = Field(..., min_length=1)
    date: str  # Format: YYYY-MM-DD
    time: str  # Format: HH:MM

class AppointmentResponse(BaseModel):
    id: int
    user_id: int
    doctor_name: str
    date: str
    time: str
    meeting_link: Optional[str] = None
    status: str
    created_at: Optional[str] = None

# Report Models
class ReportResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    upload_date: str

# Period Tracker Models
class PeriodTrackerCreate(BaseModel):
    last_period_date: str  # Format: YYYY-MM-DD

class PeriodTrackerResponse(BaseModel):
    id: int
    user_id: int
    last_period_date: str
    cycle_length: int
    next_period_date: str
    days_until_next: int
    is_late: bool
    delay_insights: Optional[list[str]] = None  # Reasons for delay

# Chatbot Models
class ChatMessage(BaseModel):
    message: str = Field(..., min_length=1)

class ChatResponse(BaseModel):
    response: str

# Health Tips Models
class HealthTipsRequest(BaseModel):
    age: Optional[int] = None
    temperature: Optional[float] = None
    humidity: Optional[float] = None  # Humidity percentage (0-100)
    air_quality_index: Optional[int] = None  # AQI (0-500)

class HealthTipsResponse(BaseModel):
    tips: list[str]
