import pytest

def test_delete_me_success(client, test_user, auth_headers):
    response = client.delete("/users/me", headers=auth_headers)
    assert response.status_code == 200
    data = response.get_json()
    assert 'message' in data

@pytest.mark.parametrize("headers, description", [
    ({}, "no auth header"),
    ({"Authorization": "Bearer invalid_token_here"}, "invalid token"),
    ({"Authorization": "InvalidFormat"}, "invalid auth format"),
])
def test_delete_me_authentication_failures(client, headers, description):
    response = client.delete("/users/me", headers=headers)
    assert response.status_code in [401, 422], f"Failed for: {description}"