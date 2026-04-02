# 🏥 CareConnect - Healthcare Web Application

A complete, beginner-friendly healthcare web application with real working features including user authentication, appointment booking, video consultations, AI chatbot, period tracking, and medical report management.

## ✨ Features

### 1. **User Authentication**
- Secure registration and login system
- Password hashing with bcrypt
- JWT token-based authentication
- Protected routes

### 2. **Dashboard**
- User profile display
- Upcoming appointments overview
- Period cycle reminders
- Personalized health tips

### 3. **Appointment System**
- Book appointments with doctors
- Automatic video call link generation (Jitsi Meet)
- View and manage appointments
- Cancel appointments

### 4. **Video Consultation** 🎥
- Real video calling using Jitsi Meet
- Unique room generation for each appointment
- One-click join from appointments list
- No additional setup required

### 5. **Health Chatbot** 🤖
- AI-powered chatbot using OpenAI API
- General health information and wellness tips
- Context-aware responses
- Quick question suggestions

### 6. **Period Tracker** 🔔
- Track menstrual cycle
- Predict next period date
- Customizable cycle length
- Late period alerts
- Period care tips

### 7. **Medical Reports** 📄
- Upload medical reports (PDF, images, documents)
- Download and view reports
- Delete reports
- Drag-and-drop file upload

### 8. **Health Tips** 💡
- Rule-based health recommendations
- Age-specific tips
- Temperature-based suggestions
- General wellness advice

## 🛠️ Tech Stack

**Backend:**
- FastAPI (Python)
- SQLite Database
- JWT Authentication
- OpenAI API Integration

**Frontend:**
- HTML5
- CSS3 (Custom styling)
- Vanilla JavaScript
- Fetch API

**Video Calling:**
- Jitsi Meet (Free, no signup required)

## 📁 Project Structure

```
CareConnect/
├── backend/
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Configuration settings
│   ├── database.py             # Database setup and connection
│   ├── models.py               # Pydantic models
│   ├── auth.py                 # Authentication utilities
│   ├── routes/
│   │   ├── users.py            # User authentication routes
│   │   ├── appointments.py     # Appointment management
│   │   ├── chatbot.py          # AI chatbot integration
│   │   ├── reports.py          # File upload/download
│   │   ├── period.py           # Period tracker
│   │   └── health_tips.py      # Health tips generator
│   ├── uploads/                # Uploaded files storage
│   └── requirements.txt        # Python dependencies
├── frontend/
│   ├── index.html              # Login page
│   ├── register.html           # Registration page
│   ├── dashboard.html          # Main dashboard
│   ├── appointment.html        # Appointments management
│   ├── chatbot.html            # AI chatbot interface
│   ├── upload.html             # Report upload
│   ├── period.html             # Period tracker
│   ├── css/
│   │   └── style.css           # Application styling
│   └── js/
│       └── utils.js            # Utility functions
└── README.md                   # This file
```

## 🚀 Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Web browser (Chrome, Firefox, Edge, Safari)

### Step 1: Install Backend Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### Step 2: Configure OpenAI API (Optional)

1. Open `backend/config.py`
2. Replace `your-openai-api-key-here` with your actual OpenAI API key
3. If you don't have an API key:
   - Visit https://platform.openai.com/api-keys
   - Create an account and generate an API key
   - **Note:** The chatbot will work with fallback responses if no API key is configured

### Step 3: Initialize Database

The database will be automatically initialized when you start the server. Alternatively, you can run:

```bash
cd backend
python database.py
```

### Step 4: Start the Backend Server

```bash
cd backend
python main.py
```

The backend API will start at: **http://localhost:8000**

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### Step 5: Open the Frontend

1. Open your web browser
2. Navigate to the frontend folder
3. Open `index.html` in your browser

**OR** use a simple HTTP server:

```bash
cd frontend

# Python 3
python -m http.server 8080

# Then visit: http://localhost:8080
```

## 📝 How to Use

### 1. Create an Account
- Go to the registration page
- Enter your name, email, and password
- Optionally add your age for personalized health tips
- Click "Register"

### 2. Login
- Enter your email and password
- Click "Login"
- You'll be redirected to the dashboard

### 3. Book an Appointment
- Go to "Appointments" page
- Fill in doctor name, date, and time
- Click "Book Appointment"
- A unique video call link will be generated automatically

### 4. Join Video Call
- Go to your appointments list
- Click "Join Video Call" button
- You'll be redirected to Jitsi Meet
- Share the link with your doctor

### 5. Use the Chatbot
- Go to "Chatbot" page
- Type your health question
- Get AI-powered responses
- Try the quick question suggestions

### 6. Track Your Period
- Go to "Period Tracker" page
- Enter your last period date
- View predictions for next period
- Customize cycle length if needed

### 7. Upload Medical Reports
- Go to "Reports" page
- Click or drag-drop to upload files
- View, download, or delete reports

## 🔧 Configuration

### Backend Configuration (`config.py`)

```python
# Security
SECRET_KEY = "your-secret-key-change-this-in-production"

# OpenAI
OPENAI_API_KEY = "your-openai-api-key-here"

# File Upload
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB
```

### Database

The SQLite database (`careconnect.db`) will be created automatically in the backend folder.

**Tables:**
- `users` - User accounts
- `appointments` - Appointment bookings
- `reports` - Uploaded medical reports
- `period_tracker` - Period cycle data

## 🎥 Video Calling

Video calls use **Jitsi Meet**, a free, open-source video conferencing solution:

- ✅ No account required
- ✅ No installation needed
- ✅ Works in any modern browser
- ✅ Unique room for each appointment

Meeting links are in the format:
```
https://meet.jit.si/careconnect-{user_id}-{appointment_id}-{unique_code}
```

## 🤖 AI Chatbot

The chatbot uses OpenAI's GPT-3.5-turbo model with a custom system prompt:

**System Prompt:**
- Provides general health information
- Offers wellness tips
- Reminds users to consult professionals
- Keeps responses concise and supportive

**Fallback Mode:**
If no API key is configured, the chatbot provides predefined helpful responses.

## 📊 API Documentation

Once the backend is running, visit:
- **Swagger UI:** http://localhost:8000/docs
- **ReDoc:** http://localhost:8000/redoc

### Key Endpoints:

**Authentication:**
- `POST /users/register` - Register new user
- `POST /users/login` - Login user
- `GET /users/me` - Get current user

**Appointments:**
- `POST /appointments` - Create appointment
- `GET /appointments` - List appointments
- `DELETE /appointments/{id}` - Cancel appointment

**Chatbot:**
- `POST /chat` - Send message to chatbot

**Reports:**
- `POST /reports/upload` - Upload report
- `GET /reports` - List reports
- `GET /reports/{id}/download` - Download report

**Period Tracker:**
- `POST /period` - Save period date
- `GET /period` - Get predictions
- `PUT /period/cycle-length` - Update cycle length

**Health Tips:**
- `POST /health-tips` - Get personalized tips

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token authentication
- ✅ Protected API endpoints
- ✅ CORS middleware configured
- ✅ File upload validation
- ✅ SQL injection protection

## 🎨 Customization

### Change Colors

Edit `frontend/css/style.css`:

```css
:root {
    --primary-color: #4f46e5;  /* Change primary color */
    --success-color: #10b981;  /* Change success color */
    --danger-color: #ef4444;   /* Change danger color */
}
```

### Modify Health Tips

Edit `backend/routes/health_tips.py` to add custom rules and tips.

### Change Video Provider

To use a different video provider (Twilio, Agora, etc.):
1. Edit `backend/routes/appointments.py`
2. Modify the `generate_meeting_link()` function
3. Update frontend to handle new link format

## 🐛 Troubleshooting

### Backend won't start
- Check if port 8000 is available
- Verify Python 3.8+ is installed
- Ensure all dependencies are installed

### Frontend can't connect to backend
- Verify backend is running on http://localhost:8000
- Check browser console for CORS errors
- Clear browser cache and reload

### Chatbot not working
- Check if OpenAI API key is configured
- Verify API key is valid and has credits
- Check backend console for error messages

### File upload fails
- Check file size (max 10MB)
- Verify file type is allowed
- Ensure uploads folder has write permissions

### Video call link not working
- Meeting links work only in modern browsers
- Ensure JavaScript is enabled
- Try in incognito/private mode

## 📱 Browser Compatibility

- ✅ Chrome 90+
- ✅ Firefox 88+
- ✅ Safari 14+
- ✅ Edge 90+

## 🚧 Future Enhancements

- [ ] Email/SMS notifications
- [ ] Multi-language support
- [ ] Mobile app version
- [ ] Doctor-side interface
- [ ] Prescription management
- [ ] Lab test results integration
- [ ] Health metrics tracking
- [ ] Export data to PDF

## 📄 License

This project is open-source and available for educational purposes.

## 🤝 Contributing

This is a beginner-friendly project. Feel free to:
- Report bugs
- Suggest features
- Submit pull requests
- Improve documentation

## 📧 Support

For questions or issues:
1. Check the troubleshooting section
2. Review API documentation at /docs
3. Check browser console for errors

## 🎉 Credits

Built with:
- FastAPI - Modern Python web framework
- Jitsi Meet - Open-source video conferencing
- OpenAI - AI language models

---

**Happy Healthcare Management! 🏥**
