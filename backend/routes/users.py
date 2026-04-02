from fastapi import APIRouter, HTTPException, status, Depends
from models import UserCreate, UserLogin, UserResponse, Token, DoctorRegister
from auth import hash_password, verify_password, create_access_token, get_current_user_id
from database import get_db

router = APIRouter(prefix="/users", tags=["users"])

@router.post("/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register(user: UserCreate):
    """Register a new patient"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (user.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and insert user
        hashed_password = hash_password(user.password)
        cursor.execute(
            "INSERT INTO users (name, email, password, age, role) VALUES (?, ?, ?, ?, ?)",
            (user.name, user.email, hashed_password, user.age, "patient")
        )
        user_id = cursor.lastrowid
        
        # Create user response
        user_response = UserResponse(
            id=user_id,
            name=user.name,
            email=user.email,
            age=user.age,
            role="patient"
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user_id)})
        
        return Token(access_token=access_token, user=user_response)

@router.post("/doctor/register", response_model=Token, status_code=status.HTTP_201_CREATED)
async def register_doctor(doctor: DoctorRegister):
    """Register a new doctor"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Check if email already exists
        cursor.execute("SELECT id FROM users WHERE email = ?", (doctor.email,))
        if cursor.fetchone():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )
        
        # Hash password and insert doctor
        hashed_password = hash_password(doctor.password)
        cursor.execute(
            """INSERT INTO users (name, email, password, role, specialization, experience) 
               VALUES (?, ?, ?, ?, ?, ?)""",
            (doctor.name, doctor.email, hashed_password, "doctor", doctor.specialization, doctor.experience)
        )
        doctor_id = cursor.lastrowid
        
        # Create user response
        user_response = UserResponse(
            id=doctor_id,
            name=doctor.name,
            email=doctor.email,
            role="doctor",
            specialization=doctor.specialization,
            experience=doctor.experience
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(doctor_id)})
        
        return Token(access_token=access_token, user=user_response)

@router.post("/login", response_model=Token)
async def login(credentials: UserLogin):
    """Login user"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Get user by email
        cursor.execute("SELECT * FROM users WHERE email = ?", (credentials.email,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Verify password
        if not verify_password(credentials.password, user["password"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )
        
        # Create user response
        user_response = UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            age=user["age"],
            role=user["role"],
            specialization=user["specialization"],
            experience=user["experience"]
        )
        
        # Create access token
        access_token = create_access_token(data={"sub": str(user["id"])})
        
        return Token(access_token=access_token, user=user_response)

@router.get("/me", response_model=UserResponse)
async def get_current_user(user_id: int = Depends(get_current_user_id)):
    """Get current user profile"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user = cursor.fetchone()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        
        return UserResponse(
            id=user["id"],
            name=user["name"],
            email=user["email"],
            age=user["age"],
            role=user["role"],
            specialization=user["specialization"],
            experience=user["experience"]
        )
