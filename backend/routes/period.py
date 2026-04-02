from fastapi import APIRouter, HTTPException, status, Depends
from models import PeriodTrackerCreate, PeriodTrackerResponse
from auth import get_current_user_id
from database import get_db
from datetime import datetime, timedelta

router = APIRouter(prefix="/period", tags=["period-tracker"])

def calculate_next_period(last_period_date: str, cycle_length: int = 28) -> dict:
    """Calculate next period date and related information"""
    # Parse last period date
    last_date = datetime.strptime(last_period_date, "%Y-%m-%d")
    
    # Calculate next period date
    next_date = last_date + timedelta(days=cycle_length)
    
    # Get current date
    current_date = datetime.now()
    
    # Calculate days until next period
    days_until = (next_date - current_date).days
    
    # Check if period is late (more than 3 days past expected date)
    is_late = days_until < -3
    
    # Generate delay insights if late
    delay_insights = None
    if is_late:
        days_late = abs(days_until)
        delay_insights = get_delay_insights(days_late)
    
    return {
        "next_period_date": next_date.strftime("%Y-%m-%d"),
        "days_until_next": days_until,
        "is_late": is_late,
        "delay_insights": delay_insights
    }

def get_delay_insights(days_late: int) -> list[str]:
    """Get possible reasons for period delay based on days late"""
    insights = []
    
    if days_late <= 7:
        insights = [
            "💡 A delay of up to 7 days can be normal due to minor cycle variations",
            "🧘 Stress or changes in routine can affect your cycle",
            "✈️ Travel or time zone changes may cause temporary irregularity",
            "⏳ Continue monitoring - this is usually not a concern"
        ]
    elif days_late <= 14:
        insights = [
            "📊 A delay of 1-2 weeks may indicate hormonal changes",
            "🏃 Intense exercise or sudden weight changes can affect your cycle",
            "😰 High stress levels may be impacting your hormonal balance",
            "💊 Some medications can cause cycle irregularity",
            "🩺 Consider consulting a healthcare provider if this persists"
        ]
    else:  # More than 2 weeks late
        insights = [
            "⚠️ A delay of more than 2 weeks warrants medical attention",
            "🤰 If sexually active, consider taking a pregnancy test",
            "🩺 Please consult a healthcare provider for proper evaluation",
            "📋 Possible causes include PCOS, thyroid issues, or other conditions",
            "💊 Bring information about any medications you're taking to your appointment"
        ]
    
    return insights

@router.post("", response_model=PeriodTrackerResponse, status_code=status.HTTP_201_CREATED)
async def save_period_data(
    period_data: PeriodTrackerCreate,
    user_id: int = Depends(get_current_user_id)
):
    """Save or update last period date"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if user already has a period tracker entry
        cursor.execute(
            "SELECT id FROM period_tracker WHERE user_id = ?",
            (user_id,)
        )
        existing = cursor.fetchone()
        
        if existing:
            # Update existing entry
            cursor.execute(
                "UPDATE period_tracker SET last_period_date = ? WHERE user_id = ?",
                (period_data.last_period_date, user_id)
            )
            tracker_id = existing["id"]
        else:
            # Insert new entry
            cursor.execute(
                "INSERT INTO period_tracker (user_id, last_period_date) VALUES (?, ?)",
                (user_id, period_data.last_period_date)
            )
            tracker_id = cursor.lastrowid
        
        # Fetch the tracker data
        cursor.execute("SELECT * FROM period_tracker WHERE id = ?", (tracker_id,))
        tracker = cursor.fetchone()
        
        # Calculate predictions
        predictions = calculate_next_period(tracker["last_period_date"], tracker["cycle_length"])
        
        return PeriodTrackerResponse(
            id=tracker["id"],
            user_id=tracker["user_id"],
            last_period_date=tracker["last_period_date"],
            cycle_length=tracker["cycle_length"],
            next_period_date=predictions["next_period_date"],
            days_until_next=predictions["days_until_next"],
            is_late=predictions["is_late"],
            delay_insights=predictions["delay_insights"]
        )

@router.get("", response_model=PeriodTrackerResponse)
async def get_period_data(user_id: int = Depends(get_current_user_id)):
    """Get period tracker data and predictions"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM period_tracker WHERE user_id = ?",
            (user_id,)
        )
        tracker = cursor.fetchone()
        
        if not tracker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No period data found. Please add your last period date."
            )
        
        # Calculate predictions
        predictions = calculate_next_period(tracker["last_period_date"], tracker["cycle_length"])
        
        return PeriodTrackerResponse(
            id=tracker["id"],
            user_id=tracker["user_id"],
            last_period_date=tracker["last_period_date"],
            cycle_length=tracker["cycle_length"],
            next_period_date=predictions["next_period_date"],
            days_until_next=predictions["days_until_next"],
            is_late=predictions["is_late"],
            delay_insights=predictions["delay_insights"]
        )

@router.put("/cycle-length", response_model=PeriodTrackerResponse)
async def update_cycle_length(
    cycle_length: int,
    user_id: int = Depends(get_current_user_id)
):
    """Update cycle length"""
    if cycle_length < 21 or cycle_length > 35:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cycle length must be between 21 and 35 days"
        )
    
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if tracker exists
        cursor.execute(
            "SELECT * FROM period_tracker WHERE user_id = ?",
            (user_id,)
        )
        tracker = cursor.fetchone()
        
        if not tracker:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No period data found"
            )
        
        # Update cycle length
        cursor.execute(
            "UPDATE period_tracker SET cycle_length = ? WHERE user_id = ?",
            (cycle_length, user_id)
        )
        
        # Fetch updated data
        cursor.execute("SELECT * FROM period_tracker WHERE user_id = ?", (user_id,))
        tracker = cursor.fetchone()
        
        # Calculate predictions
        predictions = calculate_next_period(tracker["last_period_date"], tracker["cycle_length"])
        
        return PeriodTrackerResponse(
            id=tracker["id"],
            user_id=tracker["user_id"],
            last_period_date=tracker["last_period_date"],
            cycle_length=tracker["cycle_length"],
            next_period_date=predictions["next_period_date"],
            days_until_next=predictions["days_until_next"],
            is_late=predictions["is_late"],
            delay_insights=predictions["delay_insights"]
        )
