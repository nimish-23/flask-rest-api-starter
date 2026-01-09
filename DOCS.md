# Flask Backend Boilerplate - Learning Documentation

> **Purpose**: This documentation explains all the concepts, patterns, and technologies used in this Flask backend boilerplate. Use this as a reference whenever you need to revise Flask backend development.

---

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Core Concepts](#core-concepts)
3. [File-by-File Breakdown](#file-by-file-breakdown)
4. [RESTful API Principles](#restful-api-principles)
5. [Authentication & Security](#authentication--security)
6. [Database & Models](#database--models)
7. [Validation with Marshmallow](#validation-with-marshmallow)
8. [Common Patterns](#common-patterns)

---

## Project Architecture

### Directory Structure

```
flask-backend-boilerplate/
├── app/
│   ├── __init__.py           # Application factory
│   ├── config.py             # Configuration settings
│   ├── extensions.py         # Extension initializations
│   ├── auth/
│   │   ├── __init__.py       # Blueprint export
│   │   ├── routes.py         # Authentication routes
│   │   └── schemas.py        # Validation schemas
│   └── models/
│       └── user.py           # User database model
├── instance/                 # Auto-generated database folder
├── .env                      # Environment variables (secret)
├── .env.example             # Environment template
├── .gitignore               # Git ignore rules
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── README.md                # Project overview
```

---

## Core Concepts

### 1. Application Factory Pattern

**What**: A function that creates and configures your Flask app.

**Why**:

- Allows multiple app instances (testing, development, production)
- Prevents circular imports
- Makes testing easier

**Where**: `app/__init__.py`

```python
def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    jwt.init_app(app)

    with app.app_context():
        db.create_all()

    from .auth import auth_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")

    return app
```

**Key Points**:

- Extensions are initialized with `init_app()` instead of directly
- Blueprints are registered inside the function
- Returns configured app instance

---

### 2. Blueprints

**What**: A way to organize routes into modules.

**Why**:

- Separates concerns (auth, users, posts, etc.)
- Makes code modular and reusable
- Easier to maintain large applications

**Example**: `app/auth/routes.py`

```python
auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    return jsonify({"message": "Register"})
```

**Registration**:

```python
app.register_blueprint(auth_bp, url_prefix="/auth")
# Creates routes: /auth/register, /auth/login, etc.
```

---

### 3. Extensions

**What**: Flask add-ons for extra functionality.

**Where**: `app/extensions.py`

```python
db = SQLAlchemy()      # Database ORM
jwt = JWTManager()     # JWT authentication
```

**Why Separate File**:

- Prevents circular imports
- Centralized initialization
- Can be imported anywhere

---

## File-by-File Breakdown

### `run.py` - Application Entry Point

```python
from app import create_app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True)
```

**Purpose**: Starts the Flask development server.

**How to Run**: `python run.py`

---

### `app/config.py` - Configuration

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL', 'sqlite:///test.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
```

**Key Concepts**:

- **Environment Variables**: Sensitive data stored in `.env` file
- **`load_dotenv()`**: Loads `.env` file into environment
- **Fallback Values**: `'sqlite:///test.db'` is used if `DATABASE_URL` is not set

---

### `app/extensions.py` - Extension Initialization

```python
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager

db = SQLAlchemy()
jwt = JWTManager()
```

**Why This Pattern**:

1. Create extension instances here
2. Import them in `app/__init__.py`
3. Initialize with `init_app(app)` in the factory
4. Use them anywhere in the app

---

### `app/models/user.py` - Database Model

```python
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
```

**ORM Concepts**:

- **`db.Model`**: Base class for all models
- **`db.Column`**: Database column definition
- **`primary_key=True`**: Auto-incrementing ID
- **`unique=True`**: No duplicate values
- **`nullable=False`**: Required field

---

### `app/auth/schemas.py` - Validation Schemas

```python
from marshmallow import Schema, fields, validate

class RegistrationSchema(Schema):
    username = fields.String(required=True, validate=validate.Length(min=3, max=15))
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6, max=15))
```

**Validation Features**:

- **`required=True`**: Field must be present
- **`fields.Email()`**: Validates email format
- **`validate.Length()`**: Min/max length check

---

### `app/auth/routes.py` - API Endpoints

```python
from flask import Blueprint, request, jsonify
from marshmallow import ValidationError
from .schemas import RegistrationSchema

auth_bp = Blueprint("auth", __name__)
registration_schema = RegistrationSchema()

@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        data = registration_schema.load(request.get_json())
        # Process registration...
        return jsonify({"message": "Success"}), 201
    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
```

**Flow**:

1. Receive JSON request
2. Validate with Marshmallow schema
3. Process if valid
4. Return JSON response

---

## RESTful API Principles

### HTTP Methods

| Method     | Purpose                | Example                               |
| ---------- | ---------------------- | ------------------------------------- |
| **GET**    | Retrieve data          | `GET /users` - List all users         |
| **POST**   | Create new resource    | `POST /auth/register` - Create user   |
| **PUT**    | Update entire resource | `PUT /users/1` - Update user 1        |
| **PATCH**  | Partial update         | `PATCH /users/1` - Update some fields |
| **DELETE** | Remove resource        | `DELETE /users/1` - Delete user 1     |

### Status Codes

| Code    | Meaning      | When to Use                     |
| ------- | ------------ | ------------------------------- |
| **200** | OK           | Successful GET, PUT, PATCH      |
| **201** | Created      | Successful POST                 |
| **400** | Bad Request  | Validation errors               |
| **401** | Unauthorized | Missing/invalid authentication  |
| **403** | Forbidden    | Authenticated but no permission |
| **404** | Not Found    | Resource doesn't exist          |
| **500** | Server Error | Unexpected error                |

### RESTful URL Design

✅ **Good**:

```
POST   /auth/register
POST   /auth/login
GET    /users
GET    /users/123
PUT    /users/123
DELETE /users/123
```

❌ **Bad**:

```
POST   /createUser
GET    /getUserById/123
POST   /deleteUser
```

**Rules**:

- Use nouns, not verbs
- Use plural resource names
- Use HTTP methods for actions

---

## Authentication & Security

### JWT (JSON Web Tokens)

**What**: Secure way to transmit information between client and server.

**How It Works**:

1. User logs in with credentials
2. Server validates and creates JWT token
3. Client stores token (localStorage/cookies)
4. Client sends token in headers for protected routes
5. Server validates token and grants access

**Example Login Flow**:

```python
from flask_jwt_extended import create_access_token

@auth_bp.route("/login", methods=["POST"])
def login():
    # Validate credentials
    if user and user.check_password(password):
        access_token = create_access_token(identity=user.id)
        return jsonify(access_token=access_token), 200
```

**Protected Route Example**:

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@app.route("/protected", methods=["GET"])
@jwt_required()
def protected():
    current_user_id = get_jwt_identity()
    return jsonify(user_id=current_user_id), 200
```

### Password Hashing

**Never store plain passwords!**

**Using Werkzeug**:

```python
from werkzeug.security import generate_password_hash, check_password_hash

# Hash password
hashed = generate_password_hash("mypassword")

# Verify password
is_valid = check_password_hash(hashed, "mypassword")  # True
```

**In Registration**:

```python
user = User(username=data['username'], email=data['email'])
user.password = generate_password_hash(data['password'])
db.session.add(user)
db.session.commit()
```

---

## Database & Models

### SQLAlchemy ORM

**ORM (Object-Relational Mapping)**: Write Python code instead of SQL.

**Python (ORM)**:

```python
user = User.query.filter_by(email="john@example.com").first()
```

**Equivalent SQL**:

```sql
SELECT * FROM users WHERE email = 'john@example.com' LIMIT 1;
```

### Common Database Operations

**Create**:

```python
user = User(username="john", email="john@example.com")
db.session.add(user)
db.session.commit()
```

**Read**:

```python
# Get all
users = User.query.all()

# Get by ID
user = User.query.get(1)

# Filter
user = User.query.filter_by(email="john@example.com").first()
```

**Update**:

```python
user = User.query.get(1)
user.email = "newemail@example.com"
db.session.commit()
```

**Delete**:

```python
user = User.query.get(1)
db.session.delete(user)
db.session.commit()
```

### Database Creation

**Automatic** (in `app/__init__.py`):

```python
with app.app_context():
    db.create_all()  # Creates tables based on models
```

---

## Validation with Marshmallow

### Why Validate?

**Security**: Prevent malicious data  
**Data Integrity**: Ensure correct data types  
**User Experience**: Provide clear error messages

### Schema Example

```python
from marshmallow import Schema, fields, validate, ValidationError

class RegistrationSchema(Schema):
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=15),
        error_messages={"required": "Username is required"}
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=6, max=15)
    )
```

### Using Schemas

```python
schema = RegistrationSchema()

# Valid data
data = {"username": "john", "email": "john@example.com", "password": "secret123"}
result = schema.load(data)  # Returns validated data

# Invalid data
data = {"username": "ab", "email": "invalid", "password": "123"}
try:
    result = schema.load(data)
except ValidationError as err:
    print(err.messages)
    # {"username": ["Length must be between 3 and 15."],
    #  "email": ["Not a valid email address."],
    #  "password": ["Length must be between 6 and 15."]}
```

---

## Common Patterns

### Error Handling

```python
@auth_bp.route("/register", methods=["POST"])
def register():
    try:
        # Validate
        data = schema.load(request.get_json())

        # Process
        user = User(**data)
        db.session.add(user)
        db.session.commit()

        return jsonify({"message": "Success"}), 201

    except ValidationError as err:
        return jsonify({"errors": err.messages}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
```

### Request/Response Pattern

**Request**:

```json
POST /auth/register
{
  "username": "john",
  "email": "john@example.com",
  "password": "secret123"
}
```

**Success Response**:

```json
{
  "message": "User registered successfully",
  "user": {
    "username": "john",
    "email": "john@example.com"
  }
}
```

**Error Response**:

```json
{
  "errors": {
    "email": ["Email already exists"],
    "password": ["Length must be between 6 and 15."]
  }
}
```

---

## Quick Reference Commands

### Setup

```bash
python -m venv env
env\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
```

### Run

```bash
python run.py
# Server runs on http://127.0.0.1:5000
```

### Test Endpoints

```bash
# Register
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"john","email":"john@example.com","password":"secret123"}'

# Login
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"secret123"}'
```

### Git

```bash
git add .
git commit -m "Your message"
git push origin main
```

---

## Learning Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [SQLAlchemy ORM Tutorial](https://docs.sqlalchemy.org/en/14/orm/tutorial.html)
- [Flask-JWT-Extended Docs](https://flask-jwt-extended.readthedocs.io/)
- [Marshmallow Documentation](https://marshmallow.readthedocs.io/)
- [REST API Design Best Practices](https://restfulapi.net/)

---

**Happy Learning! 🚀**
