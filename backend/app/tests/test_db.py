from app.db.database import SessionLocal
from app.models.user_model import User

def test_connection():
    db = SessionLocal()
    try:
      users = db.query(User).all()
      print("✅ Database connected, users:", users)
    except Exception as e:
        print("❌ Database connection failed:", e)  
    finally:
        db.close()  

if __name__ == "__main__":
    test_connection()