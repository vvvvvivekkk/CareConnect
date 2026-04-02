from fastapi import APIRouter, HTTPException, status, Depends
from models import DoctorResponse, TreatmentNotesCreate, TreatmentNotesResponse, AppointmentResponse
from auth import get_current_user_id
from database import get_db

router = APIRouter(prefix="/doctors", tags=["doctors"])

@router.get("", response_model=list[DoctorResponse])
async def get_doctors():
    """Get all registered doctors"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, name, email, specialization, experience 
               FROM users WHERE role = ? 
               ORDER BY experience DESC""",
            ("doctor",)
        )
        doctors = cursor.fetchall()
        
        return [
            DoctorResponse(
                id=doc["id"],
                name=doc["name"],
                email=doc["email"],
                specialization=doc["specialization"],
                experience=doc["experience"]
            )
            for doc in doctors
        ]

@router.get("/{doctor_id}", response_model=DoctorResponse)
async def get_doctor(doctor_id: int):
    """Get doctor details"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            """SELECT id, name, email, specialization, experience 
               FROM users WHERE id = ? AND role = ?""",
            (doctor_id, "doctor")
        )
        doctor = cursor.fetchone()
        
        if not doctor:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Doctor not found"
            )
        
        return DoctorResponse(
            id=doctor["id"],
            name=doctor["name"],
            email=doctor["email"],
            specialization=doctor["specialization"],
            experience=doctor["experience"]
        )

@router.get("/me/appointments", response_model=list[AppointmentResponse])
async def get_doctor_appointments(user_id: int = Depends(get_current_user_id)):
    """Get all appointments for a doctor"""
    with get_db() as conn:
        # Verify user is a doctor
        cursor = conn.cursor()
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user or user["role"] != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors can access this endpoint"
            )
        
        # Get appointments
        cursor.execute(
            """SELECT * FROM appointments 
               WHERE doctor_id = ? 
               ORDER BY date DESC, time DESC""",
            (user_id,)
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

@router.post("/appointments/{appointment_id}/notes", response_model=TreatmentNotesResponse, status_code=status.HTTP_201_CREATED)
async def add_treatment_notes(
    appointment_id: int,
    notes: TreatmentNotesCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Add treatment notes to an appointment (doctor only)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verify user is a doctor
        cursor.execute("SELECT role FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user or user["role"] != "doctor":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only doctors can add treatment notes"
            )
        
        # Verify appointment exists and belongs to this doctor
        cursor.execute(
            "SELECT id FROM appointments WHERE id = ? AND doctor_id = ?",
            (appointment_id, user_id)
        )
        if not cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        # Add treatment notes
        cursor.execute(
            """INSERT INTO treatment_notes (appointment_id, doctor_id, notes, treatment_plan, prescription)
               VALUES (?, ?, ?, ?, ?)""",
            (appointment_id, user_id, notes.notes, notes.treatment_plan, notes.prescription)
        )
        note_id = cursor.lastrowid
        
        # Fetch and return the created note
        cursor.execute("SELECT * FROM treatment_notes WHERE id = ?", (note_id,))
        result = cursor.fetchone()
        
        return TreatmentNotesResponse(
            id=result["id"],
            appointment_id=result["appointment_id"],
            doctor_id=result["doctor_id"],
            notes=result["notes"],
            treatment_plan=result["treatment_plan"],
            prescription=result["prescription"],
            created_at=result["created_at"]
        )

@router.get("/appointments/{appointment_id}/notes", response_model=TreatmentNotesResponse)
async def get_treatment_notes(
    appointment_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Get treatment notes for an appointment (patient or doctor)"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verify user is either the patient or doctor for this appointment
        cursor.execute(
            "SELECT patient_id, doctor_id FROM appointments WHERE id = ?",
            (appointment_id,)
        )
        appointment = cursor.fetchone()
        
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found"
            )
        
        if appointment["patient_id"] != user_id and appointment["doctor_id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to view these notes"
            )
        
        # Get treatment notes
        cursor.execute(
            "SELECT * FROM treatment_notes WHERE appointment_id = ?",
            (appointment_id,)
        )
        notes = cursor.fetchone()
        
        if not notes:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Treatment notes not found for this appointment"
            )
        
        return TreatmentNotesResponse(
            id=notes["id"],
            appointment_id=notes["appointment_id"],
            doctor_id=notes["doctor_id"],
            notes=notes["notes"],
            treatment_plan=notes["treatment_plan"],
            prescription=notes["prescription"],
            created_at=notes["created_at"]
        )
