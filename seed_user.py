"""
Seed initial admin user
Run: python seed_user.py
"""
from app.core.database import SessionLocal, engine, Base
from app.models.user import User

def seed_admin_user():
    # Create tables if not exist
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        # Check if user already exists
        existing = db.query(User).filter(User.email == "hyperai@hypershopcomercio.com.br").first()
        
        if existing:
            print(f"User already exists: {existing.email}")
            return
        
        # Create admin user
        admin = User(
            email="hyperai@hypershopcomercio.com.br",
            password_hash=User.hash_password("gWh28@dGcMp"),
            name="Admin HyperShop",
            role="admin",
            is_active=True
        )
        
        db.add(admin)
        db.commit()
        
        print(f"Admin user created successfully!")
        print(f"Email: hyperai@hypershopcomercio.com.br")
        print(f"Password: gWh28@dGcMp")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    seed_admin_user()
