"""
Simple Flask server runner - handles relative imports properly
"""
import sys
import os

# Add backend dir to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.main import app
from app.db import Base, engine

if __name__ == '__main__':
    # Create database tables
    Base.metadata.create_all(bind=engine)
    print("✓ Database initialized")
    print("✓ Starting Flask server on http://0.0.0.0:8000")
    print("✓ Press Ctrl+C to stop")
    
    app.run(host='0.0.0.0', port=8000, debug=True, use_reloader=False)
