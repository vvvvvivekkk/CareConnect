from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from fastapi.responses import FileResponse
from models import ReportResponse
from auth import get_current_user_id
from database import get_db
from config import settings
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/reports", tags=["reports"])

# Allowed file extensions
ALLOWED_EXTENSIONS = {'.pdf', '.jpg', '.jpeg', '.png', '.doc', '.docx'}

def get_file_extension(filename: str) -> str:
    """Get file extension"""
    return os.path.splitext(filename)[1].lower()

def is_allowed_file(filename: str) -> bool:
    """Check if file extension is allowed"""
    return get_file_extension(filename) in ALLOWED_EXTENSIONS

@router.post("/upload", response_model=ReportResponse, status_code=status.HTTP_201_CREATED)
async def upload_report(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    """Upload a medical report"""
    # Validate file
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No file provided"
        )
    
    if not is_allowed_file(file.filename):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File type not allowed. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}"
        )
    
    # Generate unique filename
    file_extension = get_file_extension(file.filename)
    unique_filename = f"{uuid.uuid4().hex}{file_extension}"
    file_path = os.path.join(settings.UPLOAD_DIR, unique_filename)
    
    # Ensure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    
    # Save file
    try:
        with open(file_path, "wb") as f:
            content = await file.read()
            
            # Check file size
            if len(content) > settings.MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"File too large. Maximum size: {settings.MAX_UPLOAD_SIZE / (1024*1024)}MB"
                )
            
            f.write(content)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Could not save file: {str(e)}"
        )
    
    # Save to database
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reports (user_id, filename, file_path) VALUES (?, ?, ?)",
            (user_id, file.filename, file_path)
        )
        report_id = cursor.lastrowid
        
        cursor.execute("SELECT * FROM reports WHERE id = ?", (report_id,))
        report = cursor.fetchone()
        
        return ReportResponse(
            id=report["id"],
            user_id=report["user_id"],
            filename=report["filename"],
            file_path=report["file_path"],
            upload_date=report["upload_date"]
        )

@router.get("", response_model=list[ReportResponse])
async def get_reports(user_id: int = Depends(get_current_user_id)):
    """Get all reports for current user"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reports WHERE user_id = ? ORDER BY upload_date DESC",
            (user_id,)
        )
        reports = cursor.fetchall()
        
        return [
            ReportResponse(
                id=report["id"],
                user_id=report["user_id"],
                filename=report["filename"],
                file_path=report["file_path"],
                upload_date=report["upload_date"]
            )
            for report in reports
        ]

@router.get("/{report_id}/download")
async def download_report(
    report_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Download a specific report"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reports WHERE id = ? AND user_id = ?",
            (report_id, user_id)
        )
        report = cursor.fetchone()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        file_path = report["file_path"]
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found on server"
            )
        
        return FileResponse(
            path=file_path,
            filename=report["filename"],
            media_type="application/octet-stream"
        )

@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    user_id: int = Depends(get_current_user_id)
):
    """Delete a report"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM reports WHERE id = ? AND user_id = ?",
            (report_id, user_id)
        )
        report = cursor.fetchone()
        
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Report not found"
            )
        
        # Delete file from disk
        file_path = report["file_path"]
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except Exception as e:
                print(f"Could not delete file: {str(e)}")
        
        # Delete from database
        cursor.execute("DELETE FROM reports WHERE id = ?", (report_id,))
