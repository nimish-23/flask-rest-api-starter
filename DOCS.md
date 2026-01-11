# Flask REST API - Comprehensive Learning Guide

> **Purpose**: This documentation serves as a complete revision guide covering all concepts, architectural patterns, problems faced, and their solutions. Use this to understand Flask backend development principles and best practices.

---

## Table of Contents

1. [Project Architecture](#project-architecture)
2. [Core Concepts](#core-concepts)
3. [File-by-File Breakdown](#file-by-file-breakdown)
4. [RESTful API Principles](#restful-api-principles)
5. [Authentication & Security](#authentication--security)
6. [Database & Migrations](#database--migrations)
7. [Validation with Marshmallow](#validation-with-marshmallow)
8. [Rate Limiting](#rate-limiting)
9. [Problems Faced & Solutions](#problems-faced--solutions)
10. [Quick Reference](#quick-reference)

---

## Project Architecture

### Final Directory Structure

```
flask-rest-api-starter/
├── app/
│   ├── __init__.py           # Application Factory
│   ├── config.py             # Environment Configuration
│   ├── extensions.py         # Extension Initializations
│   ├── models/
│   │   ├── __init__.py       # Export User model
│   │   └── user.py           # User database model
│   ├── schemas/
│   │   ├── __init__.py       # Export validation schemas
│   │   └── user_schema.py    # Marshmallow schemas
│   └── routes/
│       ├── __init__.py       # Export blueprints
│       ├── auth.py           # Auth routes
│       └── user.py           # User routes
├── migrations/               # Flask-Migrate (Alembic)
├── instance/                 # SQLite database
├── .env                      # Environment variables
├── requirements.txt          # Dependencies
└── run.py                    # Entry point
```

### Why This Structure?

**Modular Design**:

- `models/`: Database schema (what data looks like)
- `schemas/`: Validation rules (what input is valid)
- `routes/`: HTTP logic (how to respond to requests)

**Separation of Concerns**: Each directory has a single responsibility.

---

## Core Concepts

### 1. Application Factory Pattern

**What**: A function that creates and returns a configured Flask app.

**Why**:

- Enables multiple app instances (testing, dev, prod)
- Prevents circular imports
- Cleaner testing

**Code** (`app/__init__.py`):

```python
from flask import Flask
from .config import Config
from .extensions import db, jwt, limiter
from flask_migrate import Migrate

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    limiter.init_app(app)

    # Initialize migrations
    migrate = Migrate(app, db)

    # Import models after migrate
    from .models import User

    # Register blueprints
    from .routes import auth_bp, user_bp
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(user_bp, url_prefix="/users")

    return app
```

**Key Points**:

- Extensions use `init_app()` instead of direct initialization
- Blueprints registered inside function
- Models imported _after_ `Migrate` to avoid circular imports

---

### 2. Blueprints

**What**: Flask's way to organize routes into modules.

**Why**:

- Separates concerns (auth, users, posts)
- Modular and reusable
- URL prefixes for cleaner organization

**Example** (`app/routes/auth.py`):

```python
from flask import Blueprint

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    # Registration logic
    pass
```

**Registration** (`app/__init__.py`):

```python
app.register_blueprint(auth_bp, url_prefix="/auth")
# Creates: /auth/register, /auth/login, etc.
```

---

### 3. Extensions (Dependency Injection)

**What**: Third-party libraries initialized separately from the app.

**Why**: Allows sharing extensions across multiple app instances.

**Code** (`app/extensions.py`):

```python
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

db = SQLAlchemy()
jwt = JWTManager()
limiter = Limiter(key_func=get_remote_address)
```

**Usage**: Import `db`, `jwt`, `limiter` anywhere in the app.

---

## File-by-File Breakdown

### `app/config.py` - Configuration

**Purpose**: Centralize all configuration settings.

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        f"sqlite:///{os.path.abspath('instance/app.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-jwt-key")
```

**Key Concepts**:

- `load_dotenv()`: Loads `.env` file variables
- `os.getenv(key, default)`: Gets env var with fallback
- Absolute path for SQLite ensures Windows compatibility

---

### `app/models/user.py` - Database Model

**Purpose**: Define the User table schema.

```python
from app.extensions import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True, nullable=False)
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

    def to_dict(self):
        """Safely serialize user data (excludes password)"""
        return {
            "id": self.id,
            "username": self.username,
            "email": self.email,
            "created_at": self.created_at.isoformat() if self.created_at else None
        }
```

**ORM Concepts**:

- `db.Model`: Base class for all models
- `db.Column()`: Define a database column
- `primary_key=True`: Auto-incrementing ID
- `unique=True`: No duplicate values allowed
- `nullable=False`: Field is required
- `to_dict()`: Security best practice (never expose password hash)

---

### `app/schemas/user_schema.py` - Validation

**Purpose**: Validate incoming JSON data before processing.

```python
from marshmallow import Schema, fields, validate

class RegistrationSchema(Schema):
    username = fields.String(
        required=True,
        validate=validate.Length(min=3, max=15)
    )
    email = fields.Email(required=True)
    password = fields.String(
        required=True,
        validate=validate.Length(min=6)
    )

class LoginSchema(Schema):
    email = fields.Email(required=True)
    password = fields.String(required=True, validate=validate.Length(min=6))
```

**Validation Features**:

- `required=True`: Field must be present
- `fields.Email()`: Auto-validates email format
- `validate.Length(min, max)`: Length constraints

---

### `app/routes/auth.py` - Authentication Routes

**Purpose**: Handle user registration and login.

```python
from flask import Blueprint, request, jsonify
from app.extensions import db, limiter
from app.models.user import User
from app.schemas import RegistrationSchema, LoginSchema
from flask_jwt_extended import create_access_token
from werkzeug.security import generate_password_hash, check_password_hash
from marshmallow import ValidationError

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per minute")
def register():
    try:
        data = RegistrationSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    email = data.get("email")
    password = data.get("password")
    username = data.get("username")

    # Check if user exists
    if db.session.query(User).filter(
        (User.email == email) | (User.username == username)
    ).first():
        return jsonify({"error": "User already exists"}), 409

    # Hash password
    hashed_password = generate_password_hash(password)

    # Create user
    new_user = User(email=email, password=hashed_password, username=username)
    try:
        db.session.add(new_user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

    return jsonify({"message": "User registered successfully"}), 201

@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():
    try:
        data = LoginSchema().load(request.get_json())
    except ValidationError as e:
        return jsonify({"error": e.messages}), 400

    user = db.session.query(User).filter_by(email=data.get("email")).first()

    if not user or not check_password_hash(user.password, data.get("password")):
        return jsonify({"error": "Invalid credentials"}), 401

    # IMPORTANT: Convert user.id to string for JWT
    access_token = create_access_token(identity=str(user.id))
    return jsonify({"access_token": access_token, "token_type": "Bearer"}), 200
```

**Key Patterns**:

1. **Validation First**: Marshmallow catches bad data
2. **Password Hashing**: Never store plain text
3. **Error Handling**: Try/except with rollback
4. **JWT Identity**: Must be string, not int
5. **HTTP Status Codes**: 201 (created), 400 (bad request), 401 (unauthorized), 409 (conflict)

---

### `app/routes/user.py` - Protected Routes

**Purpose**: User profile endpoint (requires JWT).

```python
from flask import Blueprint, jsonify
from app.extensions import db, limiter
from app.models.user import User
from flask_jwt_extended import jwt_required, get_jwt_identity

user_bp = Blueprint("user", __name__)

@user_bp.route("/me", methods=["GET"])
@jwt_required()
@limiter.limit("10 per minute")
def get_me():
    current_user_id = get_jwt_identity()

    user = User.query.get(current_user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(user.to_dict()), 200
```

**JWT Flow**:

1. Client sends `Authorization: Bearer <token>`
2. `@jwt_required()` validates token
3. `get_jwt_identity()` extracts user ID from token
4. Query database and return user data

---

## RESTful API Principles

### HTTP Methods & Their Purposes

| Method     | Purpose          | Example Endpoint      | When                  |
| ---------- | ---------------- | --------------------- | --------------------- |
| **GET**    | Retrieve data    | `GET /users/me`       | Fetching user profile |
| **POST**   | Create resource  | `POST /auth/register` | Create new user       |
| **PUT**    | Replace resource | `PUT /users/1`        | Update entire user    |
| **PATCH**  | Partial update   | `PATCH /users/1`      | Update email only     |
| **DELETE** | Remove resource  | `DELETE /users/1`     | Delete user           |

### HTTP Status Codes

| Code    | Meaning      | Use Case                        |
| ------- | ------------ | ------------------------------- |
| **200** | OK           | Successful GET, PUT, PATCH      |
| **201** | Created      | Successful POST (new resource)  |
| **204** | No Content   | Successful DELETE               |
| **400** | Bad Request  | Validation errors               |
| **401** | Unauthorized | Missing/invalid JWT token       |
| **403** | Forbidden    | Authenticated but no permission |
| **404** | Not Found    | Resource doesn't exist          |
| **409** | Conflict     | Duplicate username/email        |
| **500** | Server Error | Unexpected error                |

### RESTful URL Design

✅ **Good (Resource-Based)**:

```
POST   /auth/register
POST   /auth/login
GET    /users/me
GET    /users/123
DELETE /users/123
```

❌ **Bad (Action-Based)**:

```
POST   /registerUser
POST   /getUserProfile
DELETE /deleteUserById/123
```

**Rules**:

- Use **nouns** for resources (`/users`, not `/getUsers`)
- Use **HTTP methods** for actions (GET, POST, DELETE)
- Use **plural nouns** (`/users`, not `/user`)

---

## Authentication & Security

### 1. Password Hashing

**Never store passwords in plain text!**

```python
from werkzeug.security import generate_password_hash, check_password_hash

# During registration
hashed = generate_password_hash("password123")
user.password = hashed

# During login
if check_password_hash(user.password, "password123"):
    # Password correct
```

**How it works**:

- Uses **bcrypt** or **pbkdf2** (one-way hashing)
- Same password = different hashes (salt added)
- Impossible to reverse-engineer

---

### 2. JWT (JSON Web Tokens)

**What**: Stateless authentication tokens.

**Structure**:

```
eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.
eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkpvaG4gRG9lIn0.
SflKxwRJSMeKKF2QT4fwpMeJf36POk6yJV_adQssw5c
```

- **Header** (algorithm)
- **Payload** (user data)
- **Signature** (verification)

**Login Flow**:

1. User sends email + password
2. Server validates credentials
3. Server creates JWT with `user.id` as identity
4. Client stores token (localStorage, cookies)

**Protected Route Flow**:

1. Client sends `Authorization: Bearer <token>`
2. `@jwt_required()` validates signature
3. `get_jwt_identity()` extracts user ID
4. Use ID to fetch user from database

**Why JWT?**:

- Stateless (no server-side session storage)
- Scalable (works across multiple servers)
- Self-contained (all info in token)

---

### 3. Rate Limiting

**Purpose**: Prevent API abuse (brute force, DoS attacks).

```python
from app.extensions import limiter

@auth_bp.route("/register", methods=["POST"])
@limiter.limit("3 per minute")  # Max 3 requests per minute
def register():
    pass
```

**How it works**:

- Tracks requests by IP address
- Returns `429 Too Many Requests` if limit exceeded
- Resets after time window

---

## Database & Migrations

### Why Flask-Migrate?

**Problem**: `db.create_all()` only works on fresh databases. It cannot:

- Add new columns to existing tables
- Rename columns
- Handle data migrations

**Solution**: Flask-Migrate (Alembic) tracks schema changes over time.

### Migration Workflow

```bash
# 1. Initialize migrations (once)
flask db init

# 2. After changing models, create migration
flask db migrate -m "Add created_at column"

# 3. Apply migration
flask db upgrade

# 4. Undo migration (if needed)
flask db downgrade
```

### Example Migration

**Before** (`app/models/user.py`):

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
```

**After**:

```python
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15))
    created_at = db.Column(db.DateTime)  # NEW
```

**Run**:

```bash
flask db migrate -m "Add created_at"
flask db upgrade
```

Alembic auto-generates SQL to add the column without losing data!

---

## Validation with Marshmallow

### Why Validate?

**Without Validation**:

```python
@app.route("/register", methods=["POST"])
def register():
    username = request.json.get("username")
    # What if username is None?
    # What if it's 100 characters long?
    # What if it contains SQL injection?
```

**With Marshmallow**:

```python
schema = RegistrationSchema()
data = schema.load(request.get_json())
# Guaranteed: username exists, 3-15 chars, string type
```

### Schema Features

```python
from marshmallow import Schema, fields, validate

class UserSchema(Schema):
    username = fields.String(
        required=True,              # Must be present
        validate=validate.Length(min=3, max=15)  # Length check
    )
    email = fields.Email(required=True)  # Email format check
    age = fields.Integer(
        validate=validate.Range(min=18, max=120)  # Range check
    )
```

### Error Handling

```python
try:
    data = RegistrationSchema().load(request.get_json())
except ValidationError as e:
    return jsonify({"error": e.messages}), 400
    # e.messages = {'username': ['Length must be between 3 and 15']}
```

---

## Rate Limiting

### Configuration

```python
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)
```

`get_remote_address`: Tracks by IP address.

### Usage

```python
@app.route("/login")
@limiter.limit("5 per minute")  # 5 requests/min per IP
def login():
    pass

@app.route("/register")
@limiter.limit("3/minute;10/hour")  # Multiple limits
def register():
    pass
```

### Why Different Limits?

- **Login** (5/min): Prevent brute force password attacks
- **Register** (3/min): Prevent bot spam
- **Profile** (10/min): Normal usage limit

---

## Problems Faced & Solutions

### Problem 1: Python 3.13.7 SQLite Readonly Error

**Error**:

```
sqlite3.OperationalError: attempt to write a readonly database
```

**Root Cause**:

- Python 3.13.7 has a compatibility issue with `db.create_all()`
- SQLite permissions not set correctly on Windows

**Attempted Fixes (Failed)**:

1. ❌ Changing database path
2. ❌ Using `check_same_thread=False`
3. ❌ Simplifying queries

**Final Solution** ✅:
Replace `db.create_all()` with **Flask-Migrate**.

**Code Change** (`app/__init__.py`):

```python
# BEFORE (broken on Python 3.13)
with app.app_context():
    db.create_all()

# AFTER (production standard)
from flask_migrate import Migrate
migrate = Migrate(app, db)
```

**Why This Works**:

- Flask-Migrate uses Alembic's internal API
- Handles SQLite properly on all Python versions
- Production-standard approach

---

### Problem 2: JWT "Subject Must Be String" Error

**Error**:

```json
{ "msg": "Subject must be a string" }
```

**Root Cause**:

```python
# user.id = 1 (integer)
access_token = create_access_token(identity=user.id)
```

Flask-JWT-Extended requires the identity to be a **string** for the JWT `sub` claim.

**Solution** ✅:

```python
access_token = create_access_token(identity=str(user.id))
```

When using `get_jwt_identity()`, convert back to int:

```python
user_id = int(get_jwt_identity())
```

---

### Problem 3: ModuleNotFoundError After Refactoring

**Error**:

```
ModuleNotFoundError: No module named 'app.utils'
```

**Cause**:
Deleted `app/utils/security.py` but forgot to remove imports.

**Solution** ✅:

1. Remove stale import:

   ```python
   # Remove this line
   from app.utils.security import hash_password

   # Use werkzeug directly
   from werkzeug.security import generate_password_hash
   ```

2. Always check imports after deleting files!

---

### Problem 4: 404 on `/user/me` (Singular vs Plural)

**Error**: `404 Not Found`

**Cause**:

```python
# In __init__.py
app.register_blueprint(user_bp, url_prefix="/users")  # Plural

# But testing with
# GET http://127.0.0.1:5000/user/me  # Singular
```

**Solution** ✅:
Use **plural** for consistency:

```
GET /users/me
```

**RESTful Convention**: Always use plural nouns (`/users`, `/posts`).

---

## Quick Reference

### Common Flask Patterns

#### 1. Blueprint Registration

```python
from .routes import auth_bp
app.register_blueprint(auth_bp, url_prefix="/auth")
```

#### 2. Protected Route

```python
@jwt_required()
def protected_route():
    user_id = get_jwt_identity()
```

#### 3. Database Query

```python
# Get by ID
user = User.query.get(user_id)

# Filter
user = User.query.filter_by(email=email).first()

# OR condition
User.query.filter((User.email == email) | (User.username == username)).first()
```

#### 4. JSON Response

```python
return jsonify({"message": "Success"}), 201
```

#### 5. Validation

```python
try:
    data = Schema().load(request.get_json())
except ValidationError as e:
    return jsonify({"error": e.messages}), 400
```

---

### Environment Variables (.env)

```
SECRET_KEY=your-secret-key-here
DATABASE_URL=sqlite:///app.db
JWT_SECRET_KEY=your-jwt-secret-here
```

Load in `config.py`:

```python
import os
from dotenv import load_dotenv

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
```

---

### Testing API Endpoints

**Register**:

```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

**Login**:

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Get Profile** (Protected):

```bash
curl -X GET http://127.0.0.1:5000/users/me \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

---

## Summary: Key Takeaways

### Architecture

✅ **Application Factory**: Creates app instances  
✅ **Blueprints**: Organize routes  
✅ **Extensions**: Shared resources (db, jwt, limiter)  
✅ **Modular Structure**: Separate models, schemas, routes

### Security

✅ **Password Hashing**: Never store plain text  
✅ **JWT Authentication**: Stateless tokens  
✅ **Rate Limiting**: Prevent abuse  
✅ **Input Validation**: Marshmallow schemas

### Database

✅ **SQLAlchemy ORM**: Python classes = database tables  
✅ **Flask-Migrate**: Schema version control  
✅ **`to_dict()` Method**: Safe serialization

### RESTful API

✅ **Resource-based URLs**: `/users`, not `/getUsers`  
✅ **HTTP Methods**: GET, POST, PUT, DELETE  
✅ **Status Codes**: 200, 201, 400, 401, 404

### Problems Solved

✅ **Python 3.13 SQLite**: Use Flask-Migrate  
✅ **JWT String Identity**: `str(user.id)`  
✅ **Module Organization**: `__init__.py` exports

---

**This project demonstrates production-ready Flask development practices. Use it as a template for building scalable REST APIs!** 🚀
