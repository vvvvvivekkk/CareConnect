from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import PlainTextResponse
from app.models import MedicalRecordCreate, MedicalRecordResponse
from app.auth import get_current_user_id
from app.database import get_db

router = APIRouter(prefix="/medical-records", tags=["medical_records"])

@router.post("", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED)
async def create_medical_record(
    record: MedicalRecordCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Doctor adds medical records after consultation"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verify user is a doctor and owns the appointment
        cursor.execute(
            "SELECT id, patient_id FROM appointments WHERE id = ? AND doctor_id = ?",
            (record.appointment_id, user_id)
        )
        appointment = cursor.fetchone()
        if not appointment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Appointment not found or you don't have permission"
            )
            
        patient_id = appointment["patient_id"]
        
        cursor.execute(
            """INSERT INTO medical_records (appointment_id, patient_id, doctor_id, diagnosis, prescription, notes)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (record.appointment_id, patient_id, user_id, record.diagnosis, record.prescription, record.notes)
        )
        record_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM medical_records WHERE id = ?", (record_id,))
        new_record = cursor.fetchone()
        
        return dict(new_record)

@router.get("", response_model=list[MedicalRecordResponse])
async def get_medical_records(user_id: int = Depends(get_current_user_id)):
    """Patient or Doctor can view medical records"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM medical_records WHERE patient_id = ? OR doctor_id = ? ORDER BY created_at DESC",
            (user_id, user_id)
        )
        records = cursor.fetchall()
        return [dict(r) for r in records]

@router.get("/{record_id}/download")
async def download_medical_report(
    record_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Generate downloadable report"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        cursor.execute(
            """SELECT mr.*, p.name as patient_name, d.name as doctor_name 
               FROM medical_records mr
               JOIN users p ON mr.patient_id = p.id
               JOIN users d ON mr.doctor_id = d.id
               WHERE mr.id = ? AND (mr.patient_id = ? OR mr.doctor_id = ?)""",
            (record_id, user_id, user_id)
        )
        record = cursor.fetchone()
        if not record:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Medical record not found"
            )
            
        report_content = f"""Medical Report
----------------------------------------
Patient Name: {record['patient_name']}
Doctor Name: {record['doctor_name']}
Date: {record['created_at']}

Diagnosis:
{record['diagnosis']}

Prescription:
{record['prescription'] or 'N/A'}

Notes:
{record['notes'] or 'N/A'}
"""
        return PlainTextResponse(
            content=report_content,
            headers={
                "Content-Disposition": f"attachment; filename=medical_report_{record_id}.txt"
            }
        )

@router.get("/analysis")
async def analyze_medical_records(user_id: int = Depends(get_current_user_id)):
    """Analyze stored medical data for potential future health risks."""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT diagnosis, notes FROM medical_records WHERE patient_id = ?",
            (user_id,)
        )
        records = cursor.fetchall()
        
        risks = set()
        
        for record in records:
            diag = (record["diagnosis"] or "").lower()
            notes = (record["notes"] or "").lower()
            combined = f"{diag} {notes}"
            
            if "high sugar" in combined or "diabetes" in combined or "glucose" in combined:
                risks.add("Potential Diabetes Risk: Keep monitoring sugar levels.")
            if "high bp" in combined or "blood pressure" in combined or "hypertension" in combined:
                risks.add("Potential Heart Risk: High blood pressure detected. Regular cardiology checkups recommended.")
            if "cholesterol" in combined:
                risks.add("Cardiovascular Risk: High cholesterol. Maintain a healthy diet.")
                
        if not risks:
            risks.add("No significant future health risks detected based on current records.")
            
        return {"health_risks": list(risks)}

