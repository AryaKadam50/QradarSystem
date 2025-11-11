#!/usr/bin/env python
"""Test script to start Flask server and validate endpoints"""
import subprocess
import time
import sys
import requests
import json
import os

# Change to backend directory
os.chdir('/Users/aryakadam/Desktop/qradar_final/backend')

# Start Flask server
print("Starting Flask server...")
server_process = subprocess.Popen(
    ['/opt/miniconda3/bin/python', 'run.py'],
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

# Give server time to start
time.sleep(5)

try:
    # Test health endpoint
    print("\n1. Testing /health endpoint...")
    response = requests.get('http://localhost:8000/health', timeout=10)
    print(f"   Status: {response.status_code}")
    print(f"   Response: {response.json()}")
    
    # Test signup endpoint
    print("\n2. Testing /auth/signup endpoint...")
    signup_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "SecurePass123!",
        "full_name": "Test User"
    }
    response = requests.post(
        'http://localhost:8000/auth/signup',
        json=signup_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    print(f"   Response: {json.dumps(response.json(), indent=2)}")
    
    # Test login endpoint
    print("\n3. Testing /auth/login endpoint...")
    login_data = {
        "username": "testuser",
        "password": "SecurePass123!"
    }
    response = requests.post(
        'http://localhost:8000/auth/login',
        json=login_data,
        headers={"Content-Type": "application/json"},
        timeout=5
    )
    print(f"   Status: {response.status_code}")
    if response.status_code == 200:
        token_response = response.json()
        access_token = token_response.get('access_token')
        print(f"   Access Token: {access_token[:50]}...")
        
        # Test profile endpoint
        print("\n4. Testing /users/me endpoint with token...")
        response = requests.get(
            'http://localhost:8000/users/me',
            headers={"Authorization": f"Bearer {access_token}"},
            timeout=5
        )
        print(f"   Status: {response.status_code}")
        print(f"   Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"   Response: {response.json()}")
    
    print("\n✅ All tests completed!")
    
except Exception as e:
    print(f"\n❌ Test failed: {str(e)}")
    import traceback
    traceback.print_exc()

finally:
    # Stop server
    print("\nStopping Flask server...")
    server_process.terminate()
    server_process.wait(timeout=5)
