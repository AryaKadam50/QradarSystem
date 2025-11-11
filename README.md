# Secure Web Application with Flask Backend and QRadar Integration

A comprehensive secure web application featuring JWT authentication, role-based access control, activity logging, and integration with IBM QRadar for security event monitoring.

## Features

### Backend (Flask)
- ✅ **User Management**: Signup and login with JWT tokens
- ✅ **Password Security**: Bcrypt hashing with 12 salt rounds
- ✅ **JWT Authentication**: Access and refresh tokens with configurable expiration
- ✅ **Role-Based Access Control**: Admin and User roles with permission checking
- ✅ **Account Lockout**: Auto-lockout after 5 failed login attempts (15-minute cooldown)
- ✅ **Activity Logging**: All actions logged with timestamp, IP, and status
- ✅ **QRadar Integration**: Send security events to QRadar via syslog
- ✅ **CORS Security**: Configurable CORS for frontend origin restriction
- ✅ **Input Validation**: Pydantic models for request validation

### Frontend (HTML/CSS/JS)
- ✅ **Responsive Design**: Mobile-friendly interface with modern CSS
- ✅ **Sign Up & Login**: Registration and authentication pages
- ✅ **User Dashboard**: Profile view and edit with password change
- ✅ **Admin Panel**: User management and activity log viewer
- ✅ **AJAX Calls**: Async API interactions via fetch
- ✅ **Notifications**: Toast notifications for user feedback

## Project Structure

```
qradar_final/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                 # Flask application and routes
│   │   ├── auth.py                 # Authentication and JWT handling
│   │   ├── models.py               # SQLAlchemy ORM models
│   │   ├── db.py                   # Database configuration
│   │   ├── qradar_logger.py        # QRadar event forwarding
│   │   ├── logger_conf.py          # Logging configuration
│   │   ├── simulate_events.py      # Event simulation for testing
│   │   ├── create_admin.py         # Admin user creation script
│   │   └── app.db                  # SQLite database (auto-created)
│   ├── .env                         # Environment variables (config)
│   ├── requirements.txt             # Python dependencies
│   ├── run.py                       # Flask development server launcher
│   └── .venv/                       # Virtual environment (optional)
├── frontend/
│   ├── index.html                  # Login/signup page
│   ├── dashboard.html              # User dashboard with admin views
│   ├── app.js                      # Frontend JavaScript logic
│   └── style.css                   # CSS styling
└── README.md                        # This file
```

## Installation & Setup

### Prerequisites
- Python 3.9+
- pip or conda
- Modern web browser (Chrome, Firefox, Safari, Edge)

### Backend Setup

1. **Clone and navigate to backend:**
   ```bash
   cd qradar_final/backend
   ```

2. **Create virtual environment (optional but recommended):**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables:**
   Edit `.env` file:
   ```
   SECRET_KEY=your-secret-key-change-this
   JWT_SECRET_KEY=your-jwt-secret-change-this
   DATABASE_URL=sqlite:///app.db
   QRADAR_HOST=your-qradar-ip-or-hostname  # (optional)
   QRADAR_PORT=514
   QRADAR_PROTOCOL=TCP
   FLASK_ENV=development
   ```

5. **Initialize database:**
   ```bash
   /opt/miniconda3/bin/python -c "
   from app.db import Base, engine
   Base.metadata.create_all(bind=engine)
   print('✓ Database initialized')
   "
   ```

6. **Start Flask server:**
   ```bash
   python run.py
   ```
   
   Server will start on `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend:**
   ```bash
   cd qradar_final/frontend
   ```

2. **Serve files (choose one method):**

   **Option A: Python HTTP Server**
   ```bash
   python -m http.server 8080
   ```

   **Option B: Node.js http-server**
   ```bash
   npx http-server -p 8080
   ```

   **Option C: Live Server (VS Code)**
   - Install "Live Server" extension in VS Code
   - Right-click `index.html` → "Open with Live Server"

3. **Access application:**
   - Open browser: `http://localhost:8080`

## API Endpoints

### Authentication
- **POST** `/auth/signup` - Register new user
  ```json
  {
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePass123!",
    "full_name": "Alice Test"
  }
  ```

- **POST** `/auth/login` - Login and get JWT tokens
  ```json
  {
    "username": "alice",
    "password": "SecurePass123!"
  }
  ```
  Returns:
  ```json
  {
    "access_token": "eyJhbGc...",
    "refresh_token": "eyJhbGc...",
    "token_type": "bearer"
  }
  ```

### User Management
- **GET** `/users/me` - Get current user profile (requires auth)
- **PUT** `/users/me` - Update user profile (requires auth)
  ```json
  {
    "email": "newemail@example.com",
    "full_name": "New Name",
    "current_password": "OldPass123!",
    "new_password": "NewPass123!"
  }
  ```

### Admin Only
- **GET** `/admin/users` - List all users (admin only)
- **GET** `/admin/logs` - View activity logs (admin only)

### Health Check
- **GET** `/health` - Server health status

## Usage Examples

### 1. Register a User
```bash
curl -X POST http://localhost:8000/auth/signup \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","email":"bob@example.com","password":"SecurePass123!","full_name":"Bob User"}'
```

### 2. Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"bob","password":"SecurePass123!"}'
```

### 3. Get Profile (with JWT token)
```bash
curl -X GET http://localhost:8000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE"
```

### 4. Update Profile
```bash
curl -X PUT http://localhost:8000/users/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN_HERE" \
  -d '{"email":"newemail@example.com","full_name":"New Name"}'
```

## Security Features

### Password Security
- **Bcrypt hashing** with 12 salt rounds
- **Password validation**: Minimum 8 characters, requires uppercase, lowercase, number, and special character
- **Password change**: Can only update password with correct current password

### Authentication
- **JWT tokens** for stateless authentication
- **Access tokens**: 24-hour expiration
- **Refresh tokens**: 7-day expiration
- **Bearer token** in Authorization header

### Account Protection
- **Failed login tracking**: Counts failed attempts per user
- **Account lockout**: Auto-lock after 5 failed attempts
- **Cooldown period**: 15-minute lockout duration
- **Session invalidation**: Tokens cannot be used after expiration

### Data Protection
- **Input validation**: Pydantic models validate all requests
- **SQL Injection prevention**: Parameterized queries via SQLAlchemy ORM
- **CORS security**: Restricted to frontend origin
- **HTTPS ready**: Can use self-signed certificates for local testing

### Activity Logging
- **All actions logged**: Signup, login, profile updates, admin access
- **Metadata captured**: Timestamp, IP address, User-Agent, action status
- **QRadar forwarding**: Security events sent via syslog to QRadar
- **Local file logging**: Events also saved to `~/.qradar_logs/secure_app.log`

## QRadar Integration

### Configuration
Set environment variables in `.env`:
```
QRADAR_HOST=192.168.1.100
QRADAR_PORT=514
QRADAR_PROTOCOL=TCP
```

### Event Types Sent
1. **LOGIN_ATTEMPT**: Successful or failed login
2. **ADMIN_ACCESS**: Admin accessing protected resources
3. **SUSPICIOUS_ACTIVITY**: Multiple failed logins, unauthorized access attempts
4. **PROFILE_UPDATE**: User profile changes

### Syslog Format
Events are formatted in RFC 5424 syslog format:
```
<134>Nov 11 15:37:23 hostname WebApp: type="LOGIN_ATTEMPT" details="{...}"
```

### Testing QRadar Events
Run the event simulator:
```bash
cd backend
python -m app.simulate_events
```

This simulates:
- 7 failed login attempts from different IPs
- Direct suspicious activity events

## Testing

### Manual Testing
1. Open `http://localhost:8080` in browser
2. Sign up with new credentials
3. Log in to get JWT tokens
4. View/edit profile
5. Create admin user and test admin panel

### Test Credentials (after setup)
```
Username: testuser
Email: test@example.com
Password: SecurePass123!
```

### Automatic Testing
```bash
# Check database
sqlite3 backend/app.db "SELECT * FROM users;"

# View activity logs
sqlite3 backend/app.db "SELECT * FROM activity_logs;"

# Check QRadar events (if configured)
cat ~/.qradar_logs/secure_app.log
```

## Self-Signed HTTPS Setup (Optional)

For local testing with HTTPS:

```bash
# Generate self-signed certificate
openssl req -x509 -newkey rsa:4096 -nodes -out cert.pem -keyout key.pem -days 365

# Update run.py to use SSL
python run.py --ssl_context=adhoc
# OR manually in run.py:
# app.run(ssl_context=('cert.pem', 'key.pem'))
```

## Troubleshooting

### Port Already in Use
```bash
# Kill existing process
lsof -ti:8000 | xargs kill -9

# Or use different port
python run.py --port 8001
```

### Database Lock
```bash
# Remove old database
rm backend/app.db

# Reinitialize
python -c "from app.db import Base, engine; Base.metadata.create_all(bind=engine)"
```

### JWT Token Issues
- Ensure `JWT_SECRET_KEY` is set in `.env`
- Check token expiration: `jwt.io` for decoding
- Verify Authorization header format: `Bearer <token>`

### CORS Issues
- Check browser console for CORS errors
- Verify frontend origin in `app/main.py` CORS config
- Update if using different port: `http://localhost:YOUR_PORT`

## Environment Variables

| Variable | Default | Purpose |
|----------|---------|---------|
| `SECRET_KEY` | dev-secret | Flask secret for session management |
| `JWT_SECRET_KEY` | dev-jwt-secret | JWT signing key |
| `DATABASE_URL` | sqlite:///app.db | Database connection string |
| `QRADAR_HOST` | None | QRadar server IP/hostname |
| `QRADAR_PORT` | 514 | Syslog port (standard: 514) |
| `QRADAR_PROTOCOL` | TCP | TCP or UDP for syslog |
| `FLASK_ENV` | development | Flask environment mode |

## Performance Notes

- **Database**: SQLite suitable for development; use PostgreSQL for production
- **Concurrent users**: Flask dev server supports ~1-5 concurrent requests
- **Production deployment**: Use Gunicorn/uWSGI + Nginx
- **Activity logs**: Automatically limited to last 500 entries in admin view

## Production Deployment

### Using Gunicorn
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app.main:app
```

### Using Docker
```dockerfile
FROM python:3.11
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app.main:app"]
```

### Environment for Production
```
SECRET_KEY=<generate-strong-random-key>
JWT_SECRET_KEY=<generate-strong-random-key>
DATABASE_URL=postgresql://user:pass@host/dbname
QRADAR_HOST=<production-qradar-ip>
FLASK_ENV=production
```

## Security Checklist

- [ ] Change `SECRET_KEY` and `JWT_SECRET_KEY` in production
- [ ] Use HTTPS with valid certificate
- [ ] Enable CORS only for trusted origins
- [ ] Use PostgreSQL instead of SQLite
- [ ] Set strong password policy
- [ ] Enable rate limiting on login endpoint
- [ ] Regular security audits and updates
- [ ] Monitor activity logs in QRadar
- [ ] Backup database regularly
- [ ] Use environment variables for secrets (not hardcoded)

## License

MIT License - Feel free to use and modify

## Support

For issues and feature requests, please create an issue in the repository.

---

**Last Updated**: November 11, 2025
**Version**: 1.0.0
**Status**: ✅ Production Ready
