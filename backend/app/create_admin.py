# backend/app/create_admin.py
from db import SessionLocal
from models import User
from auth import hash_password

# Initialize DB session
db = SessionLocal()

# Create admin user if not exists
admin_username = "admin"
admin = db.query(User).filter(User.username == admin_username).first()

if not admin:
    admin = User(
        username=admin_username,
        hashed_password=hash_password("admin123"),
        role="admin",
        full_name="System Admin",
        email="admin@example.com"
    )
    db.add(admin)
    db.commit()
    print(f"✅ Admin user created: {admin_username} / admin123")
else:
    print("⚠️ Admin user already exists")

db.close()
