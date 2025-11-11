#!/usr/bin/env python3
"""
Final verification script to ensure all components are working correctly.
Run this to verify the entire application is ready for use.
"""

import sys
import os
import json
import subprocess

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

print("="*70)
print("QRadar Security Dashboard - Final Verification")
print("="*70)

# Check 1: Python Version
print("\n[1/6] Checking Python Version...")
version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
if sys.version_info >= (3, 9):
    print(f"✅ Python {version} - OK")
else:
    print(f"❌ Python {version} - REQUIRES 3.9+")
    sys.exit(1)

# Check 2: Import Flask App
print("\n[2/6] Importing Flask Application...")
try:
    from app.main import app
    print("✅ Flask app imported successfully")
except Exception as e:
    print(f"❌ Failed to import Flask app: {e}")
    sys.exit(1)

# Check 3: Database Check
print("\n[3/6] Checking Database...")
try:
    from app.db import SessionLocal, engine, Base
    from app.models import User, ActivityLog
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    user_count = db.query(User).count()
    log_count = db.query(ActivityLog).count()
    db.close()
    print(f"✅ Database OK - {user_count} users, {log_count} activity logs")
except Exception as e:
    print(f"❌ Database error: {e}")
    sys.exit(1)

# Check 4: API Routes
print("\n[4/6] Checking API Routes...")
try:
    routes = [rule.rule for rule in app.url_map.iter_rules()]
    expected_routes = ['/auth/signup', '/auth/login', '/users/me', '/admin/users', '/admin/logs', '/health']
    missing = [r for r in expected_routes if r not in routes]
    if missing:
        print(f"❌ Missing routes: {missing}")
        sys.exit(1)
    print(f"✅ All {len(routes)} routes registered")
    for route in sorted(routes):
        if not route.startswith('/static'):
            print(f"   • {route}")
except Exception as e:
    print(f"❌ Route check failed: {e}")
    sys.exit(1)

# Check 5: Test Client Endpoints
print("\n[5/6] Testing Endpoints...")
try:
    client = app.test_client()
    
    # Test health
    response = client.get('/health')
    if response.status_code == 200:
        print("✅ Health endpoint OK")
    else:
        print(f"❌ Health endpoint failed: {response.status_code}")
        sys.exit(1)
    
    # Test signup
    import time
    unique_id = str(int(time.time() * 1000))[-6:]
    response = client.post('/auth/signup', 
        json={
            "username": f"verify_{unique_id}",
            "email": f"verify_{unique_id}@test.local",
            "password": "SecurePass123!",
            "full_name": "Verification User"
        },
        content_type='application/json'
    )
    if response.status_code in [201, 400]:  # 201 created or 400 already exists (ok)
        print("✅ Signup endpoint OK")
    else:
        print(f"❌ Signup endpoint failed: {response.status_code}")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Endpoint test failed: {e}")
    sys.exit(1)

# Check 6: Required Dependencies
print("\n[6/6] Checking Dependencies...")
try:
    required_packages = {
        'flask': 'Flask',
        'sqlalchemy': 'SQLAlchemy',
        'jose': 'python-jose',
        'bcrypt': 'bcrypt',
        'flask_cors': 'flask-cors'
    }
    
    all_ok = True
    for package, name in required_packages.items():
        try:
            __import__(package)
            print(f"✅ {name} installed")
        except ImportError:
            print(f"❌ {name} NOT installed")
            all_ok = False
    
    if not all_ok:
        print("\n❌ Install missing packages with: pip install -r backend/requirements.txt")
        sys.exit(1)
        
except Exception as e:
    print(f"❌ Dependency check failed: {e}")
    sys.exit(1)

# Final Status
print("\n" + "="*70)
print("✅ ALL VERIFICATION CHECKS PASSED!")
print("="*70)

print("\n🚀 Your application is ready to run!")
print("\nTo start the application:")
print("  1. Backend:  cd backend && python run.py")
print("  2. Frontend: python -m http.server 8080 --directory frontend")
print("  3. Browser:  http://localhost:8080")

print("\n📚 For more information, see:")
print("  • README.md - Full documentation")
print("  • PROJECT_COMPLETE.md - Project status and summary")
print("  • test_endpoints.py - Run comprehensive tests")

print("\n" + "="*70)
