# Flask REST API Starter

A production-ready Flask REST API boilerplate with JWT authentication, database migrations, rate limiting, and modular architecture.

## Features

- ✅ **Application Factory Pattern** - Scalable app initialization
- ✅ **JWT Authentication** - Secure token-based auth with Flask-JWT-Extended
- ✅ **Role-Based Access Control (RBAC)** - Admin role system with `@admin_required` decorator
- ✅ **Database Migrations** - Flask-Migrate (Alembic) for schema versioning
- ✅ **Input Validation** - Marshmallow schemas for data validation
- ✅ **Rate Limiting** - Flask-Limiter to prevent API abuse
- ✅ **Modular Architecture** - Organized routes, models, and schemas
- ✅ **Security Best Practices** - Password hashing, `to_dict()` serialization
- ✅ **Environment-based Configuration** - Separate dev/prod settings
- ✅ **Docker Support** - Production-ready Dockerfile and .dockerignore

## Project Structure

```
flask-rest-api-starter/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   ├── extensions.py        # Extension initializations (db, jwt, limiter)
│   ├── models/
│   │   ├── __init__.py      # Model exports
│   │   └── user.py          # User model (with is_admin, to_dict)
│   ├── schemas/
│   │   ├── __init__.py      # Schema exports
│   │   └── user_schema.py   # Registration, Login & Update schemas
│   ├── routes/
│   │   ├── __init__.py      # Blueprint exports
│   │   ├── auth.py          # Auth routes (register, login, logout)
│   │   └── user.py          # User routes (CRUD + list)
│   ├── utils/
│   │   └── decorators.py    # Custom decorators (@admin_required)
│   └── scripts/
│       └── create_admin.py  # Admin user creation script
├── migrations/              # Database migrations (Flask-Migrate)
├── instance/                # SQLite database (local development)
├── .env                     # Environment variables
├── requirements.txt         # Python dependencies
├── run.py                   # Application entry point
└── DOCS.md                  # Comprehensive documentation
```

## Prerequisites

- Python 3.8+ (tested on Python 3.13.7)
- pip
- virtualenv (recommended)

## Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/nimish-23/flask-rest-api-starter.git
   cd flask-rest-api-starter
   ```

2. **Create a virtual environment**

   ```bash
   python -m venv env
   ```

3. **Activate the virtual environment**
   - Windows:
     ```bash
     env\Scripts\activate
     ```
   - macOS/Linux:
     ```bash
     source env/bin/activate
     ```

4. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

5. **Set up environment variables**

   Edit `.env` and add your own secret keys:

   ```
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///app.db
   JWT_SECRET_KEY=your_jwt_secret_here
   ```

6. **Initialize the database**

   ```bash
   flask db init
   flask db migrate -m "Initial migration"
   flask db upgrade
   ```

## Running the Application

**Development mode:**

```bash
python run.py
```

The application will run on `http://127.0.0.1:5000`

**Production mode:**

```bash
gunicorn -w 4 -b 0.0.0.0:8000 run:app
```

## Docker Deployment

This project includes production-ready Docker support for easy containerization and deployment.

### Prerequisites

- Docker Desktop installed
- Docker daemon running

### Quick Start with Docker

**1. Build the Docker image:**

```bash
docker build -t flask-restapi-starter .
```

**2. Run the container:**

```bash
docker run --rm -p 5000:5000 flask-restapi-starter
```

The API will be accessible at `http://localhost:5000`

**3. Run in detached mode (background):**

```bash
docker run -d -p 5000:5000 --name flask-api flask-restapi-starter
```

**4. Stop the container:**

```bash
docker stop flask-api
```

### Docker Configuration

**Dockerfile highlights:**

- ✅ Uses `python:3.13-slim` base image for minimal footprint
- ✅ Optimized layer caching for faster rebuilds
- ✅ Environment variables configured for production
- ✅ Runs on `0.0.0.0:5000` for external accessibility
- ✅ Includes all dependencies (Flask-Migrate, SQLAlchemy, etc.)

**.dockerignore optimizations:**

- Excludes virtual environments (`env/`, `venv/`)
- Excludes test files and artifacts
- Excludes `.env` files (configure via environment variables)
- Excludes git and editor files
- Reduces image size and build time

### Environment Variables in Docker

To pass environment variables to the container:

```bash
docker run --rm -p 5000:5000 \
  -e SECRET_KEY="your-secret-key" \
  -e JWT_SECRET_KEY="your-jwt-key" \
  -e DATABASE_URL="sqlite:///app.db" \
  flask-restapi-starter
```

Or use an env file:

```bash
docker run --rm -p 5000:5000 --env-file .env.docker flask-restapi-starter
```

### Testing the Dockerized API

Once the container is running, test the endpoints:

**Check container status:**

```bash
docker ps
```

**Test the API (will return 404 for root, which is expected):**

```bash
curl http://localhost:5000/
```

**Test registration endpoint:**

```bash
curl -X POST http://localhost:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

**View container logs:**

```bash
docker logs <container-id-or-name>
```

### Production Deployment Notes

> **Warning:** The default configuration uses Flask's development server. For production deployments, consider:
>
> - Using Gunicorn as the WSGI server (modify CMD in Dockerfile)
> - Setting `debug=False` in run.py
> - Using a production database (PostgreSQL)
> - Implementing proper secret management
> - Setting up reverse proxy (Nginx)

## API Endpoints

### Authentication (`/auth`)

| Method | Endpoint         | Auth | Rate Limit | Description             |
| ------ | ---------------- | ---- | ---------- | ----------------------- |
| POST   | `/auth/register` | No   | 3/min      | Register new user       |
| POST   | `/auth/login`    | No   | 5/min      | Login and get JWT token |
| POST   | `/auth/logout`   | Yes  | -          | Logout (client-side)    |

### User (`/users`)

| Method | Endpoint    | Auth        | Rate Limit | Description                              |
| ------ | ----------- | ----------- | ---------- | ---------------------------------------- |
| GET    | `/users/me` | Yes         | 10/min     | Get current user profile                 |
| PATCH  | `/users/me` | Yes         | 10/min     | Update profile (username/email/password) |
| DELETE | `/users/me` | Yes         | 10/min     | Delete current user account              |
| GET    | `/users`    | Yes (Admin) | 10/min     | List all users (admin only, paginated)   |

> **Note:** The `GET /users` endpoint requires admin privileges (`is_admin = true`).

### Example Requests

**Register:**

```bash
curl -X POST http://127.0.0.1:5000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username":"testuser","email":"test@example.com","password":"password123"}'
```

**Login:**

```bash
curl -X POST http://127.0.0.1:5000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password123"}'
```

**Get Profile:**

```bash
curl -X GET http://127.0.0.1:5000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Update Profile:**

```bash
curl -X PATCH http://127.0.0.1:5000/users/me \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{"username":"newusername","email":"newemail@example.com"}'
```

**Delete Account:**

```bash
curl -X DELETE http://127.0.0.1:5000/users/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**List Users (with pagination):**

```bash
curl -X GET "http://127.0.0.1:5000/users?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**List Users (Admin Only):**

```bash
curl -X GET "http://127.0.0.1:5000/users?page=1&limit=10" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN"
```

## Admin Setup

Create an admin user using the interactive script:

```bash
python -m app.scripts.create_admin
```

**Example:**

```
Enter username: admin
Enter email: admin@example.com
Enter password: securepassword123

Admin user created successfully
```

The script will:

- ✅ Validate input (username min 3 chars, password min 6 chars, valid email)
- ✅ Check for duplicate username/email
- ✅ Hash password securely
- ✅ Create user with `is_admin = True`

## Configuration

Configuration is managed through environment variables in the `.env` file:

- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation

## Tech Stack

- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT authentication
- **Flask-Migrate** - Database migrations (Alembic)
- **Flask-Limiter** - Rate limiting
- **Marshmallow** - Input validation
- **Flask-CORS** - Cross-Origin Resource Sharing
- **python-dotenv** - Environment variable management
- **Gunicorn** - Production WSGI server

## Development

### Adding New Features

1. **Models**: Add to `app/models/` and update `__init__.py`
2. **Schemas**: Add to `app/schemas/` for validation
3. **Routes**: Create blueprint in `app/routes/`
4. **Register**: Import and register blueprint in `app/__init__.py`

### Database Migrations

```bash
# Create a migration after model changes
flask db migrate -m "Description of changes"

# Apply migrations
flask db upgrade

# Rollback migrations
flask db downgrade
```

## Troubleshooting

### Python 3.13+ SQLite Issues

If you encounter `readonly database` errors on Python 3.13+, ensure you're using **Flask-Migrate** instead of `db.create_all()`. This project already implements this fix.

See `DOCS.md` for detailed troubleshooting guide.

## Testing

This project includes comprehensive test coverage using **pytest**. All API endpoints are tested with various scenarios including success cases, validation errors, authentication failures, and edge cases.

### Test Structure

```
tests/
├── conftest.py              # Shared fixtures (client, test_user, auth_headers, etc.)
├── auth/
│   ├── test_register.py     # Registration endpoint tests
│   └── test_login.py        # Login endpoint tests
└── user/
    ├── test_get_user.py     # GET /users/me tests
    ├── test_update_user.py  # PATCH /users/me tests
    └── test_delete_user.py  # DELETE /users/me tests
```

### Running Tests

**Install pytest:**

```bash
pip install pytest
```

**Run all tests:**

```bash
pytest tests
```

**Run with verbose output:**

```bash
pytest tests -v
```

**Run specific test file:**

```bash
pytest tests/auth/test_register.py -v
```

**Run specific test function:**

```bash
pytest tests/auth/test_register.py::test_register_success -v
```

### Test Coverage

#### Authentication Tests (`tests/auth/`)

**Register (`test_register.py`):**

- ✅ Successful registration
- ✅ Duplicate email/username (409 Conflict)
- ✅ Invalid field values (short password, invalid email, short username)
- ✅ Missing required fields
- ✅ Wrong data types
- ✅ Invalid content type (415 Unsupported Media Type)

**Login (`test_login.py`):**

- ✅ Successful login with valid credentials
- ✅ Wrong password (401 Unauthorized)
- ✅ Non-existent user (401 Unauthorized)
- ✅ Missing email field (400 Bad Request)
- ✅ Invalid email format (400 Bad Request)

#### User Tests (`tests/user/`)

**Get Profile (`test_get_user.py`):**

- ✅ Get current user profile with valid auth
- ✅ Authentication failures (missing header, invalid token, invalid format)

**Update Profile (`test_update_user.py`):**

- ✅ Successful update (username, email, password)
- ✅ Authentication failures
- ✅ Invalid data validation (short username, invalid email, weak password)
- ✅ Valid partial updates (single field, multiple fields, empty update)

**Delete Account (`test_delete_user.py`):**

- ✅ Successful account deletion
- ✅ Authentication failures

### Common Testing Errors & Fixes

During development, we encountered and resolved several common testing issues:

#### 1️⃣ **Flask Test Client Deprecation Warning**

**Error:**

```python
# ❌ Deprecated - causes warning
assert 'message' in response.json
assert response.json['access_token'] == "..."
```

**Fix:**

```python
# ✅ Correct - use get_json() method
data = response.get_json()
assert 'message' in data
assert data['access_token'] == "..."
```

**Why:** Flask's test client `response.json` as a property is deprecated. Always use `response.get_json()` method.

#### 2️⃣ **SQLAlchemy 2.0 Query.get() Deprecation**

**Error:**

```python
# ❌ Deprecated in SQLAlchemy 2.0
user = User.query.get(user_id)
```

**Warning:**

```
LegacyAPIWarning: The Query.get() method is considered legacy as of the 1.x series
of SQLAlchemy and becomes a legacy construct in 2.0.
```

**Fix:**

```python
# ✅ SQLAlchemy 2.0 compliant
user = db.session.get(User, user_id)
```

**Files Updated:**

- `app/routes/user.py` (3 instances in `get_me()`, `patch_me()`, `delete_me()`)

#### 3️⃣ **SQLAlchemy DELETE Warning in Fixtures**

**Error:**

```
SAWarning: DELETE statement on table 'users' expected to delete 1 row(s); 0 were matched.
Please set confirm_deleted_rows=False within the mapper configuration to prevent this warning.
```

**Root Cause:** Test fixtures tried to delete users that were already deleted by the test itself.

**Fix in `conftest.py`:**

```python
@pytest.fixture(scope='function')
def test_user(app):
    with app.app_context():
        user = User(...)
        _db.session.add(user)
        _db.session.commit()
        _db.session.refresh(user)

        yield user

        # ✅ Only delete if user still exists (test might have deleted it)
        if _db.session.get(User, user.id):
            _db.session.delete(user)
            _db.session.commit()
```

**Applied to fixtures:**

- `test_user` fixture
- `admin_user` fixture

### Test Configuration

**`conftest.py` provides shared fixtures:**

- **`app`** - Flask app with test configuration (in-memory SQLite)
- **`client`** - Test client for making requests
- **`test_user`** - Pre-created test user with cleanup
- **`auth_headers`** - Valid JWT authentication headers
- **`admin_user`** - Pre-created admin user
- **`admin_headers`** - Valid admin JWT headers
- **`multiple_users`** - 15 test users for pagination testing

**Key configurations:**

```python
app.config.update({
    'TESTING': True,
    'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',  # In-memory DB
    'JWT_SECRET_KEY': 'test-secret-key',
})

# Disable rate limiting for tests
limiter.enabled = False
```

### Best Practices Implemented

✅ **Parameterized tests** - Test multiple scenarios with `@pytest.mark.parametrize`  
✅ **Proper fixtures** - Reusable components with automatic cleanup  
✅ **In-memory database** - Fast test execution with `sqlite:///:memory:`  
✅ **Rate limit disabled** - Tests run without rate limiting delays  
✅ **Descriptive test names** - Clear indication of what's being tested  
✅ **SQLAlchemy 2.0 compliance** - Future-proof code with modern APIs  
✅ **Proper JSON access** - Using `get_json()` method instead of deprecated property

## Future Enhancements

This project serves as a solid foundation for a production REST API. Potential improvements include:

### Advanced Testing

- **Code Coverage** - pytest-cov for coverage reports (`pytest --cov=app tests/`)
- **CI/CD Pipeline** - GitHub Actions for automated testing on push/PR
- **Load Testing** - Locust or Apache Bench for performance testing
- **Security Testing** - OWASP ZAP for vulnerability scanning

### API Features

- **Swagger/OpenAPI Documentation** - Interactive API docs with Flasgger
- **API Versioning** - URL-based versioning (`/api/v1/`, `/api/v2/`)
- **Advanced Pagination** - Cursor-based pagination for large datasets
- **Search & Filtering** - Query parameters for advanced filtering

### Infrastructure

- **PostgreSQL** - Production database configuration
- **Caching Layer** - Redis integration for performance
- **Logging & Monitoring** - Structured logging with ELK stack

### Security

- **Email Verification** - Confirm user emails on registration
- **Password Reset Flow** - Email-based password recovery
- **OAuth Integration** - Social login (Google, GitHub)
- **API Key Authentication** - Alternative authentication method

## License

MIT License - feel free to use this boilerplate for your projects!

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.
