from fastapi import APIRouter, HTTPException, status, Depends
from app.models import AppointmentCreate, AppointmentResponse
from app.auth import get_current_user_id
from app.database import get_db
import uuid
from datetime import datetime

router = APIRouter(prefix="/appointments", tags=["appointments"])

def generate_meeting_link(appointment_id: int) -> str:
    """Generate a unique Jitsi meeting link"""
    room_id = f"careconnect-{appointment_id}-{uuid.uuid4().hex[:8]}"
    return f"https://meet.jit.si/{room_id}"

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Create a new appointment (patient books with doctor)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verify doctor exists
        cursor.execute("SELECT id FROM users WHERE id = ? AND role = ?", (appointment.doctor_id, "doctor"))
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        # Insert appointment
        cursor.execute(
            """INSERT INTO appointments (patient_id, doctor_id, date, time, status) 
               VALUES (?, ?, ?, ?, ?)""",
            (user_id, appointment.doctor_id, appointment.date, appointment.time, "scheduled")
        )
        appointment_id = cursor.lastrowid
        
        # Generate meeting link
        meeting_link = generate_meeting_link(appointment_id)
        
        # Update appointment with meeting link
        cursor.execute(
            "UPDATE appointments SET meeting_link = ? WHERE id = ?",
            (meeting_link, appointment_id)
        )
        
        # Fetch the created appointment
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        result = cursor.fetchone()
        
        return AppointmentResponse(
            id=result["id"],
            patient_id=result["patient_id"],
            doctor_id=result["doctor_id"],
            date=result["date"],
            time=result["time"],
            meeting_link=result["meeting_link"],
            status=result["status"],
            created_at=result["created_at"]
        )

@router.get("", response_model=list[AppointmentResponse])
async def get_appointments(user_id: int = Depends(get_current_user_id)):
    """Get appointments for current user (patient or doctor)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT * FROM appointments 
               WHERE patient_id = ? OR doctor_id = ?
               ORDER BY date DESC, time DESC""",
            (user_id, user_id)
        )
        appointments = cursor.fetchall()
        
        return [
            AppointmentResponse(
                id=apt["id"],
                patient_id=apt["patient_id"],
                doctor_id=apt["doctor_id"],
                date=apt["date"],
                time=apt["time"],
                meeting_link=apt["meeting_link"],
                status=apt["status"],
                created_at=apt["created_at"]
            )
            for apt in appointments
        ]

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific appointment (if user is patient or doctor)"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM appointments WHERE id = ? AND (patient_id = ? OR doctor_id = ?)",
            (appointment_id, user_id, user_id)
        )
        appointment = cursor.fetchone()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        return AppointmentResponse(
            id=appointment["id"],
            patient_id=appointment["patient_id"],
            doctor_id=appointment["doctor_id"],
            date=appointment["date"],
            time=appointment["time"],
            meeting_link=appointment["meeting_link"],
            status=appointment["status"],
            created_at=appointment["created_at"]
        )

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Cancel an appointment (patient can cancel)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if appointment exists and user is patient
        cursor.execute(
            "SELECT id FROM appointments WHERE id = ? AND patient_id = ?",
            (appointment_id, user_id)
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Update status to cancelled
        cursor.execute(
            "UPDATE appointments SET status = ? WHERE id = ?",
            ("cancelled", appointment_id)
        )
