from fastapi import APIRouter, HTTPException, status, Depends, UploadFile, File
from app.models import ChatMessage, ChatResponse, ImageAnalysisResponse
from app.auth import get_current_user_id
from app.config import settings
from openai import OpenAI
import re
import base64

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
- Always format your response pointwise using short bullet points
- If a question is beyond your scope, kindly direct the user to consult a doctor
- Be empathetic and encouraging

Remember: You are a helpful assistant, not a replacement for professional medical advice."""


def format_pointwise_response(text: str) -> str:
    """Ensure chatbot output is returned in pointwise bullet format."""
    if not text:
        return ""

    cleaned = text.strip().replace("\r\n", "\n")
    lines = [line.strip() for line in cleaned.split("\n") if line.strip()]

    # Keep existing pointwise formatting when already present.
    if any(re.match(r"^(\d+\.|[-*•])\s+", line) for line in lines):
        return "\n".join(lines)

    compact_text = " ".join(lines)
    sentences = [
        part.strip()
        for part in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9])", compact_text)
        if part.strip()
    ]

    if len(sentences) <= 1:
        sentences = [segment.strip() for segment in re.split(r"[,;]\s+", compact_text) if segment.strip()]

    if not sentences:
        sentences = [compact_text]

    return "\n".join(f"• {sentence}" for sentence in sentences)

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
                response=format_pointwise_response(
                    "Hello! I'm your healthcare assistant. To enable AI-powered responses, please configure your OpenAI API key in the backend .env file. For now, I can tell you that maintaining a healthy lifestyle includes regular exercise, balanced diet, adequate sleep, and regular health check-ups. How can I assist you today?"
                ),
                is_fallback=True
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
        
        return ChatResponse(response=format_pointwise_response(bot_response), is_fallback=False)
        
    except Exception as e:
        # Log error and return fallback response
        error_msg = str(e)
        print(f"OpenAI API Error: {error_msg}")
        
        # Provide context-aware fallback responses based on the user's question
        user_message_lower = message.message.lower()
        
        # Check for specific health issues and provide detailed consulting advice
        
        # Stomach/digestive issues
        if any(word in user_message_lower for word in ["stomach", "gastric", "digestive", "indigestion", "nausea", "vomit"]):
            fallback = """🩺 **Stomach Pain Consultation**

**Immediate Relief Steps:**
• Avoid solid foods for a few hours; sip clear liquids (water, ginger tea)
• Apply a warm compress to your abdomen
• Lie on your left side to ease gas pain
• Avoid dairy, spicy, and fatty foods temporarily

**Possible Causes:**
• Indigestion or gas (most common)
• Food poisoning or gastritis
• Stress-related stomach issues
• Acid reflux or ulcers

**When to See a Doctor:**
• Pain lasts more than 24 hours
• Severe, sharp pain or cramping
• Blood in vomit or stool
• High fever or signs of dehydration

**Prevention Tips:**
• Eat smaller, more frequent meals
• Chew food slowly and thoroughly
• Stay hydrated throughout the day
• Manage stress through relaxation techniques

💊 Over-the-counter antacids may help, but consult a pharmacist first."""
        
        # Toothache/dental
        elif any(word in user_message_lower for word in ["tooth", "dental", "gum", "cavity", "toothache"]):
            fallback = """🦷 **Toothache Consultation**

**Immediate Relief:**
• Rinse mouth with warm salt water (1/2 tsp salt in 8oz water)
• Apply cold compress to outside of cheek (15 min on, 15 min off)
• Take over-the-counter pain reliever (ibuprofen or acetaminophen)
• Avoid hot, cold, or sweet foods that trigger pain
• Keep area clean by gentle brushing

**Possible Causes:**
• Tooth decay or cavity
• Gum infection or abscess
• Cracked tooth or damaged filling
• Food stuck between teeth
• Wisdom tooth eruption

**When to See a Dentist (Priority!):**
• Severe pain lasting more than 1-2 days
• Fever, swelling in face or jaw
• Difficulty swallowing or breathing
• Pus or bad taste in mouth
• Pain from recent dental work

**Prevention:**
• Brush twice daily with fluoride toothpaste
• Floss daily
• Limit sugary foods and drinks
• Visit dentist every 6 months

⚠️ Don't ignore dental pain - it can lead to serious infections!"""
        
        # Headache
        elif any(word in user_message_lower for word in ["headache", "migraine", "head pain"]):
            fallback = """🧠 **Headache Consultation**

**Quick Relief Methods:**
• Rest in a dark, quiet room
• Apply cold compress to forehead or back of neck
• Drink water (dehydration often causes headaches)
• Take over-the-counter pain reliever
• Try gentle neck/shoulder massage
• Practice deep breathing exercises

**Common Types & Causes:**
• **Tension headache:** Stress, poor posture, eye strain
• **Migraine:** Triggers include stress, foods, hormones, lack of sleep
• **Sinus headache:** Congestion, allergies, infection
• **Dehydration headache:** Not drinking enough water
• **Caffeine withdrawal:** Sudden reduction in caffeine intake

**When to Seek Emergency Care:**
• Sudden, severe "thunderclap" headache
• Headache with fever, stiff neck, confusion
• After head injury
• Vision changes or difficulty speaking
• Headache that worsens despite treatment

**Prevention Tips:**
• Stay hydrated (8 glasses water/day)
• Maintain regular sleep schedule
• Take breaks from screens every 20 minutes
• Practice good posture
• Manage stress through exercise or meditation
• Keep a headache diary to identify triggers

💊 For chronic headaches, consult a neurologist."""
        
        # Sleep issues
        elif any(word in user_message_lower for word in ["sleep", "insomnia", "tired", "fatigue", "sleepy"]):
            fallback = """💤 **Sleep Quality Consultation**

**Immediate Sleep Improvement Plan:**
• Set consistent bedtime and wake time (even weekends)
• Create 30-minute wind-down routine before bed
• No screens 1 hour before sleep (blue light disrupts melatonin)
• Keep bedroom cool (60-67°F / 16-19°C)
• Make room completely dark or use eye mask
• Use white noise or earplugs if needed

**Sleep Hygiene Checklist:**
✓ Limit caffeine after 2 PM
✓ Avoid alcohol before bed (disrupts deep sleep)
✓ Exercise daily but not within 3 hours of bedtime
✓ Avoid heavy meals 2-3 hours before sleep
✓ Use bed only for sleep (not work/TV)
✓ If can't sleep after 20 minutes, get up and do calm activity

**Natural Sleep Aids:**
• Chamomile or valerian root tea
• Magnesium supplement (consult doctor)
• Melatonin (short-term use, consult doctor)
• Lavender aromatherapy
• Progressive muscle relaxation

**When to See a Doctor:**
• Insomnia lasting more than 3 weeks
• Snoring with breathing pauses (sleep apnea)
• Daytime sleepiness affecting work/safety
• Nightmares or night terrors

🎯 Goal: 7-9 hours of quality sleep per night!"""
        
        # Period/menstrual issues
        elif any(word in user_message_lower for word in ["period", "menstrual", "cramp", "pms", "uterus"]):
            fallback = """🩸 **Menstrual Health Consultation**

**Cramp Relief Methods:**
• Apply heating pad to lower abdomen (20-30 min)
• Take ibuprofen or naproxen (anti-inflammatory)
• Try gentle yoga or stretching
• Take warm bath
• Light exercise (walking helps)
• Massage lower back and abdomen

**Diet for Period Relief:**
• Increase: Iron (red meat, spinach), omega-3 (fish), calcium
• Stay hydrated (reduces bloating)
• Avoid: Excess salt, caffeine, alcohol
• Try: Ginger tea, turmeric (natural anti-inflammatories)

**When to See Gynecologist:**
• Severe pain interfering with daily activities
• Heavy bleeding (changing pad/tampon every hour)
• Periods lasting more than 7 days
• Irregular cycles (shorter than 21 or longer than 35 days)
• Bleeding between periods

**Track Your Cycle:**
• Use period tracking app
• Note pain level, flow, mood changes
• Identify patterns and triggers
• Share data with doctor if needed

**PMS Management:**
• Exercise regularly
• Reduce stress
• Get adequate sleep
• Consider vitamin B6 or calcium supplements

💊 For severe cramps, ask doctor about birth control options."""
        
        # Diet/nutrition
        elif any(word in user_message_lower for word in ["diet", "food", "eat", "nutrition", "breakfast", "lunch", "dinner", "weight", "meal"]):
            fallback = """🥗 **Nutrition Consultation**

**Balanced Meal Plan:**
• **Breakfast:** Protein + whole grains + fruit
  (Example: Oatmeal with berries, nuts, and eggs)
• **Lunch:** Lean protein + vegetables + complex carbs
  (Example: Grilled chicken, quinoa, mixed greens)
• **Dinner:** Similar to lunch but lighter
  (Example: Fish, sweet potato, steamed vegetables)
• **Snacks:** Nuts, fruits, yogurt, hummus with veggies

**Portion Control Guide (Serving Sizes):**
• Protein: Palm-sized portion (3-4 oz)
• Carbs: Fist-sized portion (1 cup)
• Vegetables: 2 fist-sized portions (unlimited!)
• Fats: Thumb-sized portion (1 tbsp)

**Healthy Eating Principles:**
✓ Eat 5-6 small meals vs 3 large ones
✓ Fill half plate with vegetables
✓ Choose whole grains over refined
✓ Limit processed foods and added sugars
✓ Drink 8 glasses water daily
✓ Cook at home more often

**Foods to Include Daily:**
• Leafy greens (spinach, kale)
• Berries (antioxidants)
• Nuts and seeds (healthy fats)
• Lean proteins (chicken, fish, beans)
• Whole grains (brown rice, quinoa)
• Probiotic foods (yogurt, kimchi)

**Foods to Limit:**
• Sugary drinks and desserts
• Fried and processed foods
• White bread, pasta, rice
• High-sodium foods
• Alcohol

🎯 Aim for 80/20 rule: Eat healthy 80% of the time!"""
        
        # Exercise/fitness
        elif any(word in user_message_lower for word in ["exercise", "workout", "fitness", "gym", "training"]):
            fallback = """🏋️ **Fitness Consultation**

**Beginner Workout Plan (Weekly):**
• **Monday:** 30 min brisk walking + stretching
• **Tuesday:** 20 min bodyweight exercises (squats, push-ups, planks)
• **Wednesday:** Rest or light yoga
• **Thursday:** 30 min cycling or swimming
• **Friday:** 20 min strength training
• **Weekend:** 45 min outdoor activity (hiking, sports)

**Essential Exercise Components:**
1. **Cardio** (150 min/week):
   - Walking, running, cycling, swimming
   - Improves heart health, burns calories

2. **Strength Training** (2-3 days/week):
   - Bodyweight exercises or weights
   - Builds muscle, boosts metabolism

3. **Flexibility** (Daily):
   - Stretching or yoga
   - Prevents injury, improves mobility

4. **Balance** (2 days/week):
   - Single-leg exercises, tai chi
   - Important for older adults

**Workout Structure:**
• Warm-up: 5-10 min light cardio + dynamic stretches
• Main workout: 20-40 minutes
• Cool-down: 5-10 min stretches

**Safety Tips:**
• Start slow and progress gradually
• Stay hydrated before, during, after
• Eat small meal 1-2 hours before exercise
• Listen to your body - rest if needed
• Use proper form to prevent injury

**When to Consult Doctor Before Starting:**
• Heart disease or chest pain
• Dizziness or joint problems
• Over age 45 and sedentary
• Chronic health conditions

🎯 Goal: Move your body daily, even if just 10 minutes!"""
        
        # Mental health/stress
        elif any(word in user_message_lower for word in ["stress", "anxiety", "worried", "mental", "depression", "sad"]):
            fallback = """🧘 **Mental Health Consultation**

**Immediate Stress Relief Techniques:**
• **4-7-8 Breathing:** Inhale 4 seconds, hold 7, exhale 8 (repeat 4x)
• **Grounding Exercise:** Name 5 things you see, 4 you touch, 3 you hear, 2 you smell, 1 you taste
• **Progressive Muscle Relaxation:** Tense then release each muscle group
• **Cold water on face:** Activates calming response
• **Call a friend or family member**

**Daily Mental Wellness Routine:**
• **Morning:** 10 min meditation or journaling
• **Throughout day:** Take breaks, go outside, stretch
• **Evening:** Gratitude practice (list 3 good things)
• **Before bed:** Calming tea, no screens, relaxation

**Stress Management Strategies:**
✓ Exercise 30 min daily (natural antidepressant)
✓ Maintain social connections
✓ Practice saying "no" to overcommitment
✓ Set boundaries at work
✓ Pursue hobbies and interests
✓ Limit news and social media
✓ Get adequate sleep (7-9 hours)

**Professional Help Resources:**
• Therapy/Counseling (CBT is very effective)
• Support groups
• Crisis hotline: 988 (Suicide & Crisis Lifeline)
• Online therapy platforms (BetterHelp, Talkspace)
• Employee Assistance Program (EAP) at work

**When to Seek Professional Help:**
• Symptoms last more than 2 weeks
• Interfering with work, relationships, daily life
• Thoughts of self-harm or suicide
• Physical symptoms (chest pain, panic attacks)
• Substance use to cope

**Self-Care Activities:**
• Spend time in nature
• Practice mindfulness or meditation
• Engage in creative activities
• Listen to calming music
• Take warm baths
• Pet therapy (time with animals)

💚 Remember: Seeking help is a sign of strength, not weakness!"""
        
        # Cold/flu/fever
        elif any(word in user_message_lower for word in ["cold", "flu", "fever", "cough", "sick", "sore throat", "congestion"]):
            fallback = """🤧 **Cold & Flu Consultation**

**Symptom Relief Plan:**

**For Fever:**
• Take acetaminophen or ibuprofen as directed
• Stay cool, use light blankets
• Lukewarm bath (not cold)
• Monitor temperature every 4 hours

**For Cough:**
• Honey and warm lemon tea (natural suppressant)
• Use humidifier or steamy shower
• Elevate head while sleeping
• Avoid irritants (smoke, perfumes)
• Cough drops or lozenges

**For Congestion:**
• Saline nasal spray or rinse
• Steam inhalation (bowl of hot water + towel)
• Drink warm liquids (soup, tea)
• Sleep with extra pillow elevation

**For Sore Throat:**
• Gargle with warm salt water (1/2 tsp salt in 8oz water)
• Drink warm tea with honey
• Use throat lozenges
• Avoid irritants

**Recovery Essentials:**
• **Rest:** Get plenty of sleep
• **Hydration:** 8-10 glasses water/day
• **Nutrition:** Chicken soup, fruits high in vitamin C
• **Isolation:** Stay home to avoid spreading

**When to See a Doctor:**
• Fever over 103°F (39.4°C) or lasting >3 days
• Difficulty breathing or chest pain
• Persistent vomiting or diarrhea
• Symptoms worsen after 5-7 days
• Severe headache or stiff neck
• Confusion or altered consciousness

**Prevention for Future:**
• Wash hands frequently
• Avoid touching face
• Get annual flu vaccine
• Maintain healthy immune system (sleep, diet, exercise)
• Avoid close contact with sick people

🍵 Home remedies work best within first 48 hours of symptoms!"""
        
        else:
            # General comprehensive health advice
            fallback = """🏥 **General Health Consultation**

**Daily Health Habits Checklist:**

**Morning Routine:**
✓ Drink glass of water upon waking
✓ Eat nutritious breakfast within 1 hour
✓ Take vitamins/medications if prescribed
✓ 5-10 minutes of stretching

**Throughout the Day:**
✓ Drink water regularly (aim for 8 glasses)
✓ Eat balanced meals every 3-4 hours
✓ Take movement breaks every hour
✓ Practice good posture
✓ Manage stress with deep breathing

**Evening Routine:**
✓ Light exercise or walk
✓ Prepare healthy dinner
✓ Limit screen time before bed
✓ Wind down with relaxing activity
✓ Get 7-9 hours sleep

**Weekly Health Goals:**
• Exercise 150 minutes (30 min x 5 days)
• Meal prep for healthy eating
• Social connection (call friends/family)
• Self-care activity (hobby, relaxation)
• Review and adjust health habits

**Monthly Health Maintenance:**
• Check in with yourself: How's your energy, mood, sleep?
• Schedule any needed doctor appointments
• Restock healthy pantry items
• Try one new healthy recipe
• Review fitness progress

**When to See a Doctor:**
• Annual physical exam
• Any persistent or worsening symptoms
• New medications or concerns
• Preventive screenings based on age
• Before starting new exercise program

**Key Health Numbers to Know:**
• Blood pressure: <120/80
• Cholesterol: Total <200 mg/dL
• Blood sugar: Fasting <100 mg/dL
• BMI: 18.5-24.9 (healthy range)

🎯 Focus on progress, not perfection. Small daily habits create big results!"""
        
        # Add note about AI unavailability
        if "quota" in error_msg.lower() or "rate_limit" in error_msg.lower():
            fallback += "\n\n_Note: AI chatbot is temporarily unavailable due to API quota limits. These are general health guidelines._"
        
        return ChatResponse(response=format_pointwise_response(fallback), is_fallback=True)

@router.post("/image-analysis", response_model=ImageAnalysisResponse)
async def analyze_image(
    file: UploadFile = File(...),
    user_id: int = Depends(get_current_user_id)
):
    """Analyze uploaded image for possible health issues."""
    filename = file.filename.lower()
    
    # Try OpenAI Vision API if configured
    if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your-openai-api-key-here":
        try:
            client = OpenAI(api_key=settings.OPENAI_API_KEY)
            file_bytes = await file.read()
            base64_image = base64.b64encode(file_bytes).decode('utf-8')
            
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {
                        "role": "system",
                        "content": "You are a medical assistant performing preliminary image analysis. Return exactly two lines. First line MUST start with 'Issue: ' followed by the possible issue. Second line MUST start with 'Test: ' followed by the suggested medical test to confidently deduce the issue."
                    },
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": "Analyze this image for any visible health issues."},
                            {"type": "image_url", "image_url": {"url": f"data:{file.content_type};base64,{base64_image}"}}
                        ]
                    }
                ],
                max_tokens=200
            )
            
            content = response.choices[0].message.content
            issue, test = "Unclear visual symptoms.", "General physical examination."
            for line in content.split("\n"):
                if line.startswith("Issue: "):
                    issue = line.replace("Issue: ", "").strip()
                elif line.startswith("Test: "):
                    test = line.replace("Test: ", "").strip()
                    
            return ImageAnalysisResponse(
                possible_issue=issue,
                suggested_medical_test=test
            )
        except Exception as e:
            print(f"OpenAI Vision API Error: {str(e)}")
            
    # Fallback to simple rule-based logic based on filename
    if "skin" in filename or "rash" in filename or "red" in filename:
        return ImageAnalysisResponse(
            possible_issue="Possible dermatitis or allergic skin reaction.",
            suggested_medical_test="Dermatology consultation and allergy patching test."
        )
    elif "eye" in filename or "pink" in filename:
        return ImageAnalysisResponse(
            possible_issue="Possible conjunctivitis (pink eye).",
            suggested_medical_test="Ophthalmology exam and swab culture."
        )
    elif "throat" in filename or "tonsil" in filename:
        return ImageAnalysisResponse(
            possible_issue="Possible strep throat or tonsillitis.",
            suggested_medical_test="Rapid strep test and throat culture."
        )
    else:
        return ImageAnalysisResponse(
            possible_issue="General irregularity detected.",
            suggested_medical_test="General physical examination and blood test."
        )


