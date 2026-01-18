import pytest

def test_register_success(client, test_user):
    # test_user fixture creates a user and cleans up after test
    # We register a different user to test successful registration
    response = client.post('/auth/register', json={
        "email": "newuser@example.com",
        "password": "password123",
        "username": "newuser"
    })
    assert response.status_code == 201
    assert 'message' in response.json

def test_register_user_exists(client, test_user):
    # test_user fixture already created a user with test@example.com
    response = client.post('/auth/register', json={
        "email": "test@example.com",  # Same email as test_user
        "password": "password123",
        "username": "testuser"
    })
    assert response.status_code == 409
    assert 'error' in response.json

# ===== Invalid Field Values =====
@pytest.mark.parametrize("email,password,username,description", [
    ("invalid-email", "password123", "testuser", "invalid email format"),
    ("test@example.com", "12345", "testuser", "short password"),
    ("test@example.com", "password123", "ab", "short username"),
    ("", "password123", "testuser", "empty email"),
    ("test@example.com", "", "testuser", "empty password"),
    ("test@example.com", "password123", "", "empty username"),
])
def test_register_invalid_field_values(client, email, password, username, description):
    """Test registration with invalid field values"""
    response = client.post('/auth/register', json={
        "email": email,
        "password": password,
        "username": username
    })
    assert response.status_code == 400, f"Failed for: {description}"
    assert 'error' in response.json

# ===== Missing Required Fields =====
@pytest.mark.parametrize("data,description", [
    ({"password": "password123", "username": "testuser"}, "missing email"),
    ({"email": "test@example.com", "username": "testuser"}, "missing password"),
    ({"email": "test@example.com", "password": "password123"}, "missing username"),
    ({}, "empty body"),
])
def test_register_missing_fields(client, data, description):
    """Test registration with missing required fields"""
    response = client.post('/auth/register', json=data)
    assert response.status_code == 400, f"Failed for: {description}"
    assert 'error' in response.json

# ===== Wrong Data Types =====
@pytest.mark.parametrize("email,password,username,description", [
    (12345, "password123", "testuser", "email not string"),
    ("test@example.com", None, "testuser", "password is None"),
    ("test@example.com", "password123", 12345, "username not string"),
])
def test_register_wrong_data_types(client, email, password, username, description):
    """Test registration with wrong data types"""
    response = client.post('/auth/register', json={
        "email": email,
        "password": password,
        "username": username
    })
    assert response.status_code == 400, f"Failed for: {description}"
    assert 'error' in response.json

# ===== Duplicate User =====
def test_register_duplicate_username(client, test_user):
    """Test registration with existing username but different email"""
    response = client.post('/auth/register', json={
        "email": "different@example.com",
        "password": "password123",
        "username": "testuser"  # Same username as test_user
    })
    assert response.status_code == 409
    assert 'error' in response.json

# ===== Invalid Content Type =====
def test_register_wrong_content_type(client):
    """Test registration with plain text instead of JSON"""
    response = client.post('/auth/register', data="not json data", content_type='text/plain')
    # Flask returns 415 (Unsupported Media Type) for wrong content type
    assert response.status_code == 415, "Should reject non-JSON content type"

def test_register_none_json_body(client):
    """Test registration with None as JSON body"""
    response = client.post('/auth/register', json=None)
    # Flask returns 415 (Unsupported Media Type) for None as JSON
    assert response.status_code == 415, "Should reject None as JSON body"