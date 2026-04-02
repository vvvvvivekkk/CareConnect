# CareConnect

CareConnect is a FastAPI-based healthcare web application for patients and doctors. It includes authentication, appointment booking, doctor dashboards, treatment notes, medical report uploads, a period tracker, health tips, and a chatbot for general wellness guidance.

## Features

- Patient registration, login, and profile lookup with JWT auth
- Doctor registration and doctor directory pages
- Appointment booking with automatic Jitsi Meet links
- Doctor dashboard with appointments and treatment notes
- Medical report upload, download, and deletion
- Period tracking with next-cycle predictions
- Rule-based health tips based on age and environmental factors
- Chatbot endpoint with OpenAI support and fallback responses when no API key is configured
- HTML pages served by FastAPI with static CSS and JavaScript assets

## Tech Stack

- Backend: FastAPI, SQLite, SQLAlchemy, Pydantic, JWT, bcrypt
- Frontend: Jinja2 templates, HTML, CSS, vanilla JavaScript
- Integrations: OpenAI, Jitsi Meet

## Project Layout

```text
CareConnect/
├── run.py               # Main entry point
├── app/
│   ├── main.py          # FastAPI application
│   ├── config.py        # Settings and environment variables
│   ├── database.py      # SQLite setup and migrations
│   ├── models.py        # Pydantic request/response models
│   ├── auth.py          # Password hashing and JWT helpers
│   ├── routes/          # API and page routes
│   ├── static/          # CSS, JS, and images
│   ├── templates/       # HTML pages
│   └── uploads/         # Uploaded report files
├── requirements.txt
└── README.md
```

## Local Setup

### Prerequisites

- Python 3.8 or newer
- pip

### Install Dependencies

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### Configure Environment Variables

Create a `.env` file in the project root if you want to override defaults:

```env
SECRET_KEY=replace-this-in-production
OPENAI_API_KEY=your-openai-api-key
```

`OPENAI_API_KEY` is optional. If it is not set, the chatbot returns fallback responses.

### Run the App

```bash
python run.py
```

The app runs at:

- Web app: http://localhost:8000
- API docs: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

You can also start it directly with uvicorn:

```bash
uvicorn app.main:app --reload
```

## Main Pages

- `/` or `/login` - Login page
- `/register` - Registration page
- `/dashboard` - Patient dashboard
- `/appointments` - Appointment management
- `/doctors` - Doctor directory
- `/doctor-dashboard` - Doctor dashboard
- `/chatbot` - Chatbot UI
- `/period` - Period tracker
- `/reports` or `/upload` - Medical reports page

## API Endpoints

All API routes are mounted under `/api`.

### Authentication

- `POST /api/users/register`
- `POST /api/users/doctor/register`
- `POST /api/users/login`
- `GET /api/users/me`

### Doctors

- `GET /api/doctors`
- `GET /api/doctors/{doctor_id}`
- `GET /api/doctors/me/appointments`
- `POST /api/doctors/appointments/{appointment_id}/notes`
- `GET /api/doctors/appointments/{appointment_id}/notes`

### Appointments

- `POST /api/appointments`
- `GET /api/appointments`
- `GET /api/appointments/{appointment_id}`
- `DELETE /api/appointments/{appointment_id}`

### Chatbot

- `POST /api/chat`

### Reports

- `POST /api/reports/upload`
- `GET /api/reports`
- `GET /api/reports/{report_id}/download`
- `DELETE /api/reports/{report_id}`

### Period Tracker

- `POST /api/period`
- `GET /api/period`
- `PUT /api/period/cycle-length`

### Health Tips

- `POST /api/health-tips`
- `GET /api/health-tips`

### Health Check

- `GET /api/health`

## Database

The application uses SQLite and creates `app/careconnect.db` automatically on startup.

Tables include:

- `users`
- `appointments`
- `treatment_notes`
- `reports`
- `period_tracker`

## Notes

- Uploaded reports are stored in `app/uploads/`.
- Appointment links use Jitsi Meet room URLs.
- The chatbot falls back to predefined guidance if OpenAI is unavailable or not configured.

## Troubleshooting

- If the server does not start, confirm that Python 3.8+ is installed and port 8000 is free.
- If login fails, delete any stale `careconnect.db` file only if you want to reset local data.
- If file uploads fail, check the file type and size limit of 10 MB.# 🏥 CareConnect - Healthcare Web Application

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

## ⚡ Quick Run Commands (Windows)

Run these commands in two terminals.

### Terminal 1 (Backend API)

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Terminal 2 (Frontend)

```bash
cd frontend
python -m http.server 8080
```

If port 8080 is already in use on your machine, run:

```bash
python -m http.server 8081
```

Open in browser:
- Frontend: http://localhost:8080
- Backend API: http://localhost:8000
- Swagger docs: http://localhost:8000/docs

If you started frontend on 8081, use: http://localhost:8081

## 🔌 Ports To Open

For local development, make sure these ports are allowed in firewall/security settings:

- `8000` (Backend FastAPI server)
- `8080` (Frontend static server)
- `8081` (Alternative frontend port if 8080 is occupied)

Optional/External service ports:
- `443` outbound (HTTPS for OpenAI API and Jitsi Meet)
- `80` outbound (HTTP redirects if any)

If you are running only on your own machine, `localhost` access is usually enough and no router/NAT changes are required.

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
