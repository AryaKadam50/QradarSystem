# 🚀 Quick Start Guide

## ⚡ 5-Minute Setup

### Step 1: Start Backend (Terminal 1)
```bash
cd /Users/aryakadam/Desktop/qradar_final/backend
python run.py
```

You should see:
```
✓ Database initialized
✓ Starting Flask server on http://0.0.0.0:8000
Press CTRL+C to stop the server
```

**✅ Backend is running on http://localhost:8000**

---

### Step 2: Start Frontend (Terminal 2)
```bash
cd /Users/aryakadam/Desktop/qradar_final/frontend
python -m http.server 8080
```

You should see:
```
Serving HTTP on 0.0.0.0 port 8080 (http://0.0.0.0:8080/) ...
```

**✅ Frontend is running on http://localhost:8080**

---

### Step 3: Open in Browser
Open your web browser and go to:
```
http://localhost:8080
```

**✅ Application is ready!**

---

## 🎯 Try It Out

### Create a New Account
1. Click **"Sign Up"** button
2. Fill in the form:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `SecurePass123!`
   - Full Name: `Test User`
3. Click **"Sign Up"**

### Login
1. Enter your credentials
2. Click **"Login"**
3. You'll be redirected to your dashboard

### View Your Profile
1. Click **"Profile"** tab
2. See your user information
3. Click **"Edit Profile"** to change your name

### Try Admin Features (if you have admin account)
- Create admin user first (see below)
- Login with admin account
- Click **"Admin"** tab to see:
  - User List
  - Activity Logs

---

## 👨‍💼 Create Admin Account (Optional)

Run this in a new terminal:

```bash
cd /Users/aryakadam/Desktop/qradar_final
python -c "
import sys
sys.path.insert(0, 'backend')
from app.db import SessionLocal, engine, Base
from app.models import User

Base.metadata.create_all(bind=engine)
db = SessionLocal()

# Check if admin already exists
if db.query(User).filter(User.username == 'admin').first():
    print('✅ Admin user already exists: admin / AdminPass123!')
else:
    admin = User(
        username='admin',
        email='admin@qradar.local',
        full_name='Administrator',
        role='admin',
        is_active=True
    )
    admin.set_password('AdminPass123!')
    db.add(admin)
    db.commit()
    print('✅ Admin user created: admin / AdminPass123!')
"
```

---

## 📋 Test All Endpoints

```bash
python test_endpoints.py
```

This will test all 7 endpoints and show results.

---

## ✅ Verify Everything Works

```bash
python verify_setup.py
```

This will check:
- Python version
- Flask app
- Database
- Routes
- Dependencies

---

## 🔌 API Examples

### Health Check
```bash
curl http://localhost:8000/health
```

### Signup
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username":"alice",
    "email":"alice@example.com",
    "password":"SecurePass123!",
    "full_name":"Alice"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"alice","password":"SecurePass123!"}'
```

Returns:
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

### Get Profile (replace TOKEN with actual token)
```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/users/me
```

---

## 🎓 What's Included

✅ **Backend**
- Flask REST API with 8 endpoints
- JWT authentication
- Bcrypt password security
- SQLite database
- QRadar integration

✅ **Frontend**
- Login/Signup page
- User dashboard
- Profile management
- Admin panel

✅ **Tests**
- Comprehensive endpoint tests
- System verification script

✅ **Documentation**
- README.md (full docs)
- PROJECT_COMPLETE.md (status)
- SUMMARY.md (project overview)
- QUICK_START.md (this file)

---

## 🔧 Troubleshooting

### Port 8000 already in use
```bash
# Kill the process using port 8000
lsof -ti:8000 | xargs kill -9

# Then start again
python run.py
```

### Port 8080 already in use
```bash
# Use different port
python -m http.server 8888 --directory frontend

# Then open http://localhost:8888
```

### Login fails
- Double-check username and password
- If account is locked, wait 15 minutes
- Verify account was created with signup

### "Cannot connect to QRadar"
This is normal if QRadar is not configured. The app works without it.

### Database locked
```bash
# Delete and recreate database
rm backend/app.db
python run.py
```

---

## 🎯 Default Credentials

After creating the admin user above:

**Admin Account:**
- Username: `admin`
- Password: `AdminPass123!`
- Access: All endpoints + admin panel

**Create Custom Users:**
- Use signup page or `/auth/signup` endpoint
- Users are created with role `user`
- Only users with role `admin` can access admin endpoints

---

## 📚 Learn More

For detailed documentation:
- **README.md** - Full API documentation with examples
- **PROJECT_COMPLETE.md** - Project status and features
- **SUMMARY.md** - Detailed project overview

---

## ✨ Key Features

🔐 **Security**
- JWT authentication
- Bcrypt password hashing
- Account lockout protection
- Role-based access control

📊 **Monitoring**
- Activity logging
- Login tracking with IP
- QRadar integration

👥 **User Management**
- Sign up and login
- Profile view/edit
- Password change
- Admin user listing

🔧 **Developer Friendly**
- Clean Flask API
- Well-documented code
- Comprehensive tests
- Easy to extend

---

## 🚀 You're All Set!

Your secure web application is ready to use.

**Next Steps:**
1. ✅ Run `python run.py` (backend)
2. ✅ Run `python -m http.server 8080 --directory frontend` (frontend)
3. ✅ Open http://localhost:8080 in browser
4. ✅ Sign up and explore!

---

**Happy coding! 🎉**
