from app import create_app
from app.extensions import db
from app.models.user import User
from werkzeug.security import generate_password_hash
from app.schemas import RegistrationSchema
from marshmallow import ValidationError


def create_admin():
    """Interactive script to create or promote admin users"""
    app = create_app()
    
    with app.app_context():
        
        try:
            data = RegistrationSchema().load({
                "username": input("Enter username: ").strip(),
                "email": input("Enter email: ").strip(),
                "password": input("Enter password: ").strip(),
            })
        except ValidationError as e:
            print("Validation error:", e.messages)
            return

        username = data["username"]
        email = data["email"]
        hashed_password = generate_password_hash(data["password"])

        user = User.query.filter((User.username == username) | (User.email == email)).first()

        if user:
            return print("User already exists")

        new_user = User(username=username, email=email, password=hashed_password)
        new_user.is_admin = True

        try:
            db.session.add(new_user)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print("Failed to create admin user:", str(e))
            return

        print("Admin user created successfully")

if __name__ == "__main__":
    create_admin()
