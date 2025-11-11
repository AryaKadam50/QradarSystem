#!/usr/bin/env python
"""
Flask application entry point.
Run with: python run.py
"""
import sys
import os

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.db import Base, engine

if __name__ == '__main__':
    # Initialize database
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")
    print("✓ Starting Flask server on http://0.0.0.0:8000")
    print("\nPress CTRL+C to stop the server")
    
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
