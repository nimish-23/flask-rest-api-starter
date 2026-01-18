import pytest

def test_update_me_success(client, test_user, auth_headers):
    response = client.patch("/users/me", json={
        'email':'newemail@example.com',
        'username':'newusername',
        'password':'newpassword'
    }, headers=auth_headers)
    
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data
    assert 'user' in data  

@pytest.mark.parametrize("headers, description", [
    ({}, "no auth header"),
    ({"Authorization": "Bearer invalid_token_here"}, "invalid token"),
    ({"Authorization": "InvalidFormat"}, "invalid auth format"),
])
def test_update_me_authentication_failures(client, headers, description):
    response = client.patch("/users/me", headers=headers)
    assert response.status_code in [401, 422], f"Failed for: {description}" 

@pytest.mark.parametrize("data", [
    {"username": "ab"},
    {"email": "invalid_email"},
    {"password": "123"},
])
def test_update_user_invalid_data(client, auth_headers, data):
    response = client.patch("/users/me", json=data, headers=auth_headers)
    assert response.status_code == 400

@pytest.mark.parametrize("data", [
    {},  # no update
    {"username": "validname"},
    {"email": "valid@example.com"},
    {"password": "validpassword"},
])
def test_update_user_valid_data(client, auth_headers, data):
    response = client.patch("/users/me", json=data, headers=auth_headers)
    assert response.status_code == 200
