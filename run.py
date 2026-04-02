#!/usr/bin/env python
"""
CareConnect - Healthcare Web Application
Run this file to start the application.

Usage:
    python run.py

Or directly with uvicorn:
    uvicorn app.main:app --reload
"""

if __name__ == "__main__":
    import uvicorn
    
    print("🏥 Starting CareConnect...")
    print("📍 Server running at: http://localhost:8000")
    print("📚 API docs at: http://localhost:8000/docs")
    print("-" * 50)
    
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
