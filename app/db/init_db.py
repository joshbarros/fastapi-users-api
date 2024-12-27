from sqlalchemy.orm import Session
from app.crud.user import create_user
from app.db.base import SessionLocal, Base, engine
from app.models.user import User

# Initial test users
INITIAL_USERS = [
    {"username": "user", "password": "L0XuwPOdS5U", "role": "user"},
    {"username": "admin", "password": "JKSipm0YH", "role": "admin"},
]

def init_db(db: Session) -> None:
    # Create tables
    Base.metadata.create_all(bind=engine)
    
    # Check if we already have users
    user = db.query(User).first()
    if user is not None:
        print("Database already initialized")
        return

    for user_data in INITIAL_USERS:
        user = create_user(
            db=db,
            username=user_data["username"],
            password=user_data["password"],
            role=user_data["role"]
        )
        print(f"Created user: {user.username} with role: {user.role}")

def main() -> None:
    db = SessionLocal()
    init_db(db)

if __name__ == "__main__":
    main()
