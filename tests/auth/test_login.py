import pytest

def test_login_success(client, test_user):
    """Test successful login with valid credentials."""
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'access_token' in data
    assert data['token_type'] == 'Bearer'


def test_login_wrong_password(client, test_user):
    """Test login fails with wrong password."""
    response = client.post('/auth/login', json={
        'email': 'test@example.com',
        'password': 'wrongpassword123'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == 'Invalid credentials'


def test_login_user_not_found(client):
    """Test login fails when user doesn't exist."""
    response = client.post('/auth/login', json={
        'email': 'nonexistent@example.com',
        'password': 'password123'
    })
    
    assert response.status_code == 401
    data = response.get_json()
    assert data['error'] == 'Invalid credentials'


def test_login_missing_email(client):
    """Test login fails when email is missing."""
    response = client.post('/auth/login', json={
        'password': 'password123'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data


def test_login_invalid_email_format(client):
    """Test login fails with invalid email format."""
    response = client.post('/auth/login', json={
        'email': 'not-an-email',
        'password': 'password123'
    })
    
    assert response.status_code == 400
    data = response.get_json()
    assert 'error' in data
