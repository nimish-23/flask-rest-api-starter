import pytest
from app import create_app
from app.extensions import db as _db
from app.models.user import User
from werkzeug.security import generate_password_hash


@pytest.fixture(scope='session')
def app():
    """Create Flask app for testing."""
    from app.extensions import limiter  # Import here to access limiter
    
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': 'sqlite:///:memory:',
        'JWT_SECRET_KEY': 'test-secret-key',
    })
    
    # Disable rate limiting for tests
    limiter.enabled = False
    
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
        
        # Only delete if user still exists (test might have deleted it)
        if _db.session.get(User, user.id):
            _db.session.delete(user)
            _db.session.commit()


@pytest.fixture(scope='function')
def auth_headers(client, test_user):
    """Get authentication headers for test_user."""
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    data = response.get_json()
    token = data['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def admin_user(app):
    """Create an admin user."""
    with app.app_context():
        admin = User(
            email='admin@example.com',
            username='admin',
            password=generate_password_hash('password123'),
            is_admin=True
        )
        _db.session.add(admin)
        _db.session.commit()
        _db.session.refresh(admin)
        
        yield admin
        
        # Only delete if admin still exists (test might have deleted it)
        if _db.session.get(User, admin.id):
            _db.session.delete(admin)
            _db.session.commit()


@pytest.fixture(scope='function')
def admin_headers(client, admin_user):
    """Get authentication headers for admin_user."""
    response = client.post('/auth/login', json={
        'email': 'admin@example.com',
        'password': 'password123'
    })
    data = response.get_json()
    token = data['access_token']
    return {'Authorization': f'Bearer {token}'}


@pytest.fixture(scope='function')
def multiple_users(app):
    """Create multiple users for pagination testing."""
    with app.app_context():
        users = []
        for i in range(15):
            user = User(
                email=f'user{i}@example.com',
                username=f'user{i}',
                password=generate_password_hash('password123')
            )
            _db.session.add(user)
            users.append(user)
        
        _db.session.commit()
        for user in users:
            _db.session.refresh(user)
        
        yield users
        
        for user in users:
            _db.session.delete(user)
        _db.session.commit()
