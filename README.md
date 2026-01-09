# Flask Backend Boilerplate

A clean, reusable Flask backend boilerplate with JWT authentication, SQLAlchemy, and essential configurations pre-configured.

## Features

- ✅ Application Factory Pattern
- ✅ JWT Authentication with Flask-JWT-Extended
- ✅ SQLAlchemy ORM
- ✅ Environment-based Configuration
- ✅ Clean Project Structure
- ✅ Ready for Development & Production

## Project Structure

```
flask-backend-boilerplate/
├── app/
│   ├── __init__.py          # Application factory
│   ├── config.py            # Configuration settings
│   └── extensions.py        # Extension initializations
├── .env.example             # Environment variables template
├── .gitignore              # Git ignore rules
├── requirements.txt        # Python dependencies
└── run.py                  # Application entry point
```

## Prerequisites

- Python 3.8+
- pip
- virtualenv (recommended)

## Installation

1. **Clone the repository**

   ```bash
   git clone <your-repo-url>
   cd flask-backend-boilerplate
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
   ```bash
   cp .env.example .env
   ```
   Edit `.env` and add your own secret keys:
   ```
   SECRET_KEY=your_secret_key_here
   DATABASE_URL=sqlite:///test.db
   JWT_SECRET_KEY=your_jwt_secret_here
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

## Configuration

Configuration is managed through environment variables in the `.env` file:

- `SECRET_KEY`: Flask secret key for sessions
- `DATABASE_URL`: Database connection string
- `JWT_SECRET_KEY`: Secret key for JWT token generation

## Tech Stack

- **Flask** - Web framework
- **SQLAlchemy** - ORM
- **Flask-JWT-Extended** - JWT authentication
- **Flask-CORS** - Cross-Origin Resource Sharing
- **python-dotenv** - Environment variable management
- **Gunicorn** - Production WSGI server

## Next Steps

1. Add your models in `app/models/`
2. Create routes/blueprints in `app/routes/`
3. Register blueprints in `app/__init__.py`
4. Add database migrations with Flask-Migrate (optional)

## License

MIT License - feel free to use this boilerplate for your projects!

## Contributing

Contributions are welcome! Feel free to submit a Pull Request.
