from fastapi import APIRouter, HTTPException, status, Depends
from models import ChatMessage, ChatResponse
from auth import get_current_user_id
from config import settings
from openai import OpenAI

router = APIRouter(prefix="/chat", tags=["chatbot"])

# System prompt for the healthcare chatbot
SYSTEM_PROMPT = """You are a helpful healthcare assistant for CareConnect, a healthcare web application. 
Your role is to:
- Provide general health information and wellness tips
- Answer basic health-related questions
- Offer supportive guidance for common health concerns
- Remind users about healthy lifestyle practices

Important guidelines:
- Always remind users to consult healthcare professionals for medical diagnoses and treatment
- Never provide specific medical diagnoses or prescribe medications
- Keep responses concise, supportive, and easy to understand
- If a question is beyond your scope, kindly direct the user to consult a doctor
- Be empathetic and encouraging

Remember: You are a helpful assistant, not a replacement for professional medical advice."""

@router.post("", response_model=ChatResponse)
async def chat(
    message: ChatMessage,
    user_id: int = Depends(get_current_user_id)
):
    """Send message to chatbot and get response"""
    try:
        # Check if API key is configured
        if settings.OPENAI_API_KEY == "your-openai-api-key-here":
            # Return a fallback response if API key is not configured
            return ChatResponse(
                response="Hello! I'm your healthcare assistant. To enable AI-powered responses, please configure your OpenAI API key in the backend config.py file. For now, I can tell you that maintaining a healthy lifestyle includes regular exercise, balanced diet, adequate sleep, and regular health check-ups. How can I assist you today?"
            )
        
        # Initialize OpenAI client
        client = OpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Call OpenAI API
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": message.message}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        # Extract response
        bot_response = response.choices[0].message.content
        
        return ChatResponse(response=bot_response)
        
    except Exception as e:
        # Log error and return fallback response
        print(f"OpenAI API Error: {str(e)}")
        return ChatResponse(
            response="I'm having trouble connecting to my knowledge base right now. Here's some general advice: Stay hydrated, get regular exercise, eat a balanced diet, and don't hesitate to consult a healthcare professional for specific concerns. Is there something specific I can help you with?"
        )
