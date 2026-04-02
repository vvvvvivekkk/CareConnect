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


def get_appointments_columns(cursor) -> set[str]:
    cursor.execute("PRAGMA table_info(appointments)")
    return {column[1] for column in cursor.fetchall()}


def appointment_to_response(appointment) -> AppointmentResponse:
    patient_id = appointment["patient_id"] if "patient_id" in appointment.keys() else appointment["user_id"]
    return AppointmentResponse(
        id=appointment["id"],
        patient_id=patient_id,
        doctor_id=appointment["doctor_id"],
        date=appointment["date"],
        time=appointment["time"],
        meeting_link=appointment["meeting_link"],
        status=appointment["status"],
        created_at=appointment["created_at"]
    )


def ensure_meeting_link(cursor, appointment_row) -> str:
    meeting_link = appointment_row["meeting_link"]
    if meeting_link:
        return meeting_link

    meeting_link = generate_meeting_link(appointment_row["id"])
    cursor.execute(
        "UPDATE appointments SET meeting_link = ? WHERE id = ?",
        (meeting_link, appointment_row["id"])
    )
    return meeting_link

@router.post("", response_model=AppointmentResponse, status_code=status.HTTP_201_CREATED)
async def create_appointment(
    appointment: AppointmentCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Create a new appointment (patient books with doctor)"""
    with get_db() as conn:
        cursor = conn.cursor()
        appointment_columns = get_appointments_columns(cursor)
        
        # Verify doctor exists
        cursor.execute("SELECT id, name FROM users WHERE id = ? AND role = ?", (appointment.doctor_id, "doctor"))
        doctor = cursor.fetchone()
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )

        doctor_name = doctor["name"]
        
        # Insert appointment
        if "user_id" in appointment_columns:
            if "doctor_name" in appointment_columns:
                cursor.execute(
                    """INSERT INTO appointments (user_id, doctor_name, patient_id, doctor_id, date, time, status) 
                       VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (user_id, doctor_name, user_id, appointment.doctor_id, appointment.date, appointment.time, "scheduled")
                )
            else:
                cursor.execute(
                    """INSERT INTO appointments (user_id, patient_id, doctor_id, date, time, status) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (user_id, user_id, appointment.doctor_id, appointment.date, appointment.time, "scheduled")
                )
        else:
            if "doctor_name" in appointment_columns:
                cursor.execute(
                    """INSERT INTO appointments (doctor_name, patient_id, doctor_id, date, time, status) 
                       VALUES (?, ?, ?, ?, ?, ?)""",
                    (doctor_name, user_id, appointment.doctor_id, appointment.date, appointment.time, "scheduled")
                )
            else:
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
        ensure_meeting_link(cursor, result)
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        result = cursor.fetchone()

        return appointment_to_response(result)

@router.get("", response_model=list[AppointmentResponse])
async def get_appointments(user_id: int = Depends(get_current_user_id)):
    """Get appointments for current user (patient or doctor)"""
    with get_db() as conn:
        cursor = conn.cursor()
        appointment_columns = get_appointments_columns(cursor)
        patient_clause = "patient_id = ?"
        params = [user_id, user_id]

        if "user_id" in appointment_columns:
            patient_clause = "(patient_id = ? OR user_id = ?)"
            params = [user_id, user_id, user_id]

        cursor.execute(
            f"""SELECT * FROM appointments 
               WHERE {patient_clause} OR doctor_id = ?
               ORDER BY date DESC, time DESC""",
            tuple(params)
        )
        appointments = cursor.fetchall()

        for appointment in appointments:
            ensure_meeting_link(cursor, appointment)

        cursor.execute(
            f"""SELECT * FROM appointments 
               WHERE {patient_clause} OR doctor_id = ?
               ORDER BY date DESC, time DESC""",
            tuple(params)
        )
        appointments = cursor.fetchall()
        
        return [appointment_to_response(apt) for apt in appointments]

@router.get("/{appointment_id}", response_model=AppointmentResponse)
async def get_appointment(
    appointment_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Get a specific appointment (if user is patient or doctor)"""
    with get_db() as conn:
        cursor = conn.cursor()
        appointment_columns = get_appointments_columns(cursor)
        if "user_id" in appointment_columns:
            cursor.execute(
                "SELECT * FROM appointments WHERE id = ? AND (patient_id = ? OR user_id = ? OR doctor_id = ?)",
                (appointment_id, user_id, user_id, user_id)
            )
        else:
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

        ensure_meeting_link(cursor, appointment)
        cursor.execute("SELECT * FROM appointments WHERE id = ?", (appointment_id,))
        appointment = cursor.fetchone()
        
        return appointment_to_response(appointment)

@router.delete("/{appointment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def cancel_appointment(
    appointment_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Cancel an appointment (patient can cancel)"""
    with get_db() as conn:
        cursor = conn.cursor()
        appointment_columns = get_appointments_columns(cursor)
        
        # Check if appointment exists and user is patient
        if "user_id" in appointment_columns:
            cursor.execute(
                "SELECT id FROM appointments WHERE id = ? AND (patient_id = ? OR user_id = ?)",
                (appointment_id, user_id, user_id)
            )
        else:
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
