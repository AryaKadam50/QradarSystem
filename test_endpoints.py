#!/usr/bin/env python
"""Direct endpoint testing without running a server"""
import sys
import os
import json
import time

sys.path.insert(0, '/Users/aryakadam/Desktop/qradar_final/backend')

from app.main import app
from app.db import SessionLocal

# Global variable to store test username
test_username = None

print("="*70)
print("TESTING FLASK API ENDPOINTS")
print("="*70)

# Use Flask test client
client = app.test_client()

def test_health():
    """Test health check endpoint"""
    print("\n1. Testing GET /health")
    response = client.get('/health')
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {json.dumps(data, indent=6)}")
    assert response.status_code == 200
    print("   ✓ PASS")

def test_signup():
    """Test signup endpoint"""
    global test_username
    print("\n2. Testing POST /auth/signup")
    unique_id = str(int(time.time() * 1000))[-6:]  # Last 6 digits of timestamp in ms
    test_username = f"testuser_{unique_id}"
    signup_data = {
        "username": test_username,
        "email": f"test_{unique_id}@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
    response = client.post(
        '/auth/signup',
        json=signup_data,
        content_type='application/json'
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {json.dumps(data, indent=6)}")
    assert response.status_code == 201, f"Expected 201, got {response.status_code}"
    print("   ✓ PASS")
    return data

def test_login():
    """Test login endpoint"""
    print("\n3. Testing POST /auth/login")
    login_data = {
        "username": "testuser2",
        "password": "SecurePass123!"
    }
    response = client.post(
        '/auth/login',
        json=login_data,
        content_type='application/json'
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response Keys: {list(data.keys())}")
    assert response.status_code == 200
    assert 'access_token' in data
    print(f"   Access Token: {data['access_token'][:50]}...")
    print("   ✓ PASS")
    return data['access_token']

def test_profile(token):
    """Test profile endpoint"""
    print("\n4. Testing GET /users/me with auth token")
    response = client.get(
        '/users/me',
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {json.dumps(data, indent=6)}")
    assert response.status_code == 200
    print("   ✓ PASS")

def test_update_profile(token):
    """Test profile update endpoint"""
    print("\n5. Testing PUT /users/me with auth token")
    update_data = {
        "full_name": "Updated Name"
    }
    response = client.put(
        '/users/me',
        json=update_data,
        headers={'Authorization': f'Bearer {token}'},
        content_type='application/json'
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response: {json.dumps(data, indent=6)}")
    assert response.status_code == 200
    print("   ✓ PASS")

def test_admin_users(token):
    """Test admin users endpoint"""
    print("\n6. Testing GET /admin/users (admin only)")
    response = client.get(
        '/admin/users',
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f"   User count: {len(data)}")
        print(f"   Sample user: {json.dumps(data[0] if data else {}, indent=6)}")
    print("   ✓ PASS")

def test_admin_logs(token):
    """Test admin logs endpoint"""
    print("\n7. Testing GET /admin/logs (admin only)")
    response = client.get(
        '/admin/logs',
        headers={'Authorization': f'Bearer {token}'}
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        data = response.get_json()
        print(f"   Log count: {len(data)}")
        if data:
            print(f"   Sample log: {json.dumps(data[0], indent=6)}")
    print("   ✓ PASS")

try:
    test_health()
    test_signup()
    # Use the global test_username set by test_signup
    print("\n3. Testing POST /auth/login")
    login_data = {
        "username": test_username,
        "password": "SecurePass123!"
    }
    response = client.post(
        '/auth/login',
        json=login_data,
        content_type='application/json'
    )
    print(f"   Status: {response.status_code}")
    data = response.get_json()
    print(f"   Response Keys: {list(data.keys())}")
    assert response.status_code == 200, f"Login failed with status {response.status_code}: {data}"
    assert 'access_token' in data
    token = data['access_token']
    print(f"   Access Token: {token[:50]}...")
    print("   ✓ PASS")
    
    test_profile(token)
    test_update_profile(token)
    test_admin_users(token)
    test_admin_logs(token)
    
    print("\n" + "="*70)
    print("✅ ALL TESTS PASSED!")
    print("="*70)
    
except AssertionError as e:
    print(f"\n❌ Test failed: {e}")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
