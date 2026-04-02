from fastapi import APIRouter, Depends
from models import HealthTipsRequest, HealthTipsResponse
from auth import get_current_user_id

router = APIRouter(prefix="/health-tips", tags=["health-tips"])

def generate_health_tips(age: int = None, temperature: float = None, 
                         humidity: float = None, air_quality_index: int = None) -> list[str]:
    """Generate rule-based health tips based on multiple factors"""
    tips = []
    
    # Age-based tips
    if age:
        if age < 18:
            tips.extend([
                "🥤 Drink at least 8 glasses of water daily for proper hydration",
                "😴 Get 8-10 hours of sleep each night for healthy growth",
                "🏃 Stay active with at least 60 minutes of physical activity daily",
                "🥗 Eat plenty of fruits, vegetables, and whole grains"
            ])
        elif 18 <= age <= 60:
            tips.extend([
                "💧 Stay hydrated - drink water throughout the day",
                "🧘 Practice stress management through meditation or yoga",
                "🥗 Maintain a balanced diet with proteins, carbs, and healthy fats",
                "🏋️ Exercise regularly - aim for 150 minutes per week",
                "😴 Get 7-9 hours of quality sleep each night"
            ])
        else:  # age > 60
            tips.extend([
                "🦴 Focus on bone health with calcium and vitamin D",
                "🚶 Stay active with low-impact exercises like walking or swimming",
                "🩺 Schedule regular health check-ups and screenings",
                "🧠 Keep your mind active with puzzles and social activities",
                "💊 Take medications as prescribed and track your health metrics"
            ])
    
    # Temperature-based tips (body temperature in Fahrenheit)
    if temperature:
        if temperature > 99.0:  # Fever (> 99°F)
            tips.extend([
                "🌡️ You may have a fever. Rest and stay hydrated",
                "💊 Consider taking fever-reducing medication if recommended",
                "🩺 Monitor your temperature and consult a doctor if it persists",
                "🛏️ Get plenty of rest to help your body recover"
            ])
        elif temperature < 97.0:  # Low body temperature
            tips.extend([
                "🧥 Keep warm with appropriate clothing and blankets",
                "☕ Drink warm fluids to help regulate body temperature",
                "🩺 If this persists, consult a healthcare provider"
            ])
        else:  # Normal temperature
            tips.append("✅ Your temperature is normal - keep maintaining healthy habits!")
    
    # Humidity-based tips
    if humidity is not None:
        if humidity < 30:  # Very dry
            tips.extend([
                "💧 Low humidity detected! Drink extra water to stay hydrated",
                "🧴 Use moisturizer to prevent dry skin",
                "👃 Consider using a humidifier to prevent respiratory irritation"
            ])
        elif humidity > 70:  # Very humid
            tips.extend([
                "💨 High humidity! Stay cool and avoid strenuous outdoor activities",
                "🏠 Use air conditioning or dehumidifier if available",
                "🚿 Shower regularly to prevent skin issues"
            ])
        else:
            tips.append("✅ Humidity levels are comfortable - ideal for outdoor activities!")
    
    # Air Quality Index (AQI) based tips
    if air_quality_index is not None:
        if air_quality_index > 150:  # Unhealthy
            tips.extend([
                "😷 Poor air quality! Wear a mask outdoors",
                "🏠 Stay indoors as much as possible",
                "🪟 Keep windows closed to prevent pollution entry",
                "🫁 If you have respiratory conditions, use prescribed medications"
            ])
        elif air_quality_index > 100:  # Moderate to unhealthy for sensitive groups
            tips.extend([
                "⚠️ Moderate air quality - sensitive groups should limit outdoor exposure",
                "🏃 Avoid intense outdoor exercise",
                "🏠 Consider indoor activities today"
            ])
        elif air_quality_index <= 50:
            tips.append("✅ Air quality is good - great day for outdoor activities!")
    
    # General tips (always included if few specific tips)
    general_tips = [
        "🚭 Avoid smoking and limit alcohol consumption",
        "🧼 Wash your hands regularly to prevent infections",
        "😊 Take care of your mental health - it's as important as physical health",
        "👨‍⚕️ Don't hesitate to consult healthcare professionals when needed"
    ]
    
    # Add general tips if we have few specific tips
    if len(tips) < 4:
        tips.extend(general_tips[:2])
    
    return tips

@router.post("", response_model=HealthTipsResponse)
async def get_health_tips(
    request: HealthTipsRequest,
    user_id: int = Depends(get_current_user_id)
):
    """Get personalized health tips based on age, temperature, humidity, and air quality"""
    tips = generate_health_tips(
        age=request.age, 
        temperature=request.temperature,
        humidity=request.humidity,
        air_quality_index=request.air_quality_index
    )
    return HealthTipsResponse(tips=tips)

@router.get("", response_model=HealthTipsResponse)
async def get_general_tips(user_id: int = Depends(get_current_user_id)):
    """Get general health tips"""
    tips = [
        "💧 Drink at least 8 glasses of water daily",
        "🏃 Aim for 30 minutes of physical activity most days",
        "😴 Get 7-9 hours of quality sleep each night",
        "🥗 Eat a balanced diet with plenty of fruits and vegetables",
        "🧘 Practice stress management through relaxation techniques",
        "🩺 Schedule regular health check-ups",
        "🧼 Wash your hands frequently to prevent illness",
        "😊 Take care of your mental health - talk to someone if needed"
    ]
    return HealthTipsResponse(tips=tips)
