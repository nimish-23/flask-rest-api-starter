import pytest

def test_get_me_success(client, test_user, auth_headers):
    """Test getting current user profile with valid authentication"""
    response = client.get('/users/me', headers=auth_headers)
    
    assert response.status_code == 200
    assert response.json['id'] == test_user.id
    assert response.json['username'] == 'testuser'
    assert response.json['email'] == 'test@example.com'


@pytest.mark.parametrize("headers,description", [
    ({}, "no auth header"),
    ({"Authorization": "Bearer invalid_token_here"}, "invalid token"),
    ({"Authorization": "InvalidFormat"}, "invalid auth format"),
])
def test_get_me_authentication_failures(client, headers, description):
    """Test authentication failures for GET /users/me"""
    response = client.get('/users/me', headers=headers)
    
    # Should return 401 (unauthorized) or 422 (unprocessable entity for invalid token)
    assert response.status_code in [401, 422], f"Failed for: {description}"

