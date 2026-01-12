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

## Future Enhancements

This project serves as a solid foundation for a production REST API. Potential improvements include:

### Testing

- **Unit Tests** - pytest for testing models and utilities
- **Integration Tests** - Test API endpoints with test database
- **Code Coverage** - pytest-cov for coverage reports
- **CI/CD Pipeline** - GitHub Actions for automated testing

### API Features

- **Swagger/OpenAPI Documentation** - Interactive API docs with Flasgger
- **API Versioning** - URL-based versioning (`/api/v1/`, `/api/v2/`)
- **Advanced Pagination** - Cursor-based pagination for large datasets
- **Search & Filtering** - Query parameters for advanced filtering

### Infrastructure

- **Docker Support** - Dockerfile and docker-compose.yml
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
