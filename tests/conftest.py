import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create Flask app for testing."""
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key'
    })
    
    with app.app_context():
        _db.create_all()
        yield app
        _db.drop_all()


@pytest.fixture(scope='function')
def client(app):
    """Test client."""
    return app.test_client()


@pytest.fixture(scope='function')
def test_user(app):
    """Create test user."""
    with app.app_context():
        user = User(
            email='test@example.com',
            username='testuser',
            password=generate_password_hash('password123')
        )
        _db.session.add(user)
        _db.session.commit()
        _db.session.refresh(user)
        
        yield user
        
        _db.session.delete(user)
        _db.session.commit()
