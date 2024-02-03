import pytest

@pytest.mark.parametrize("email, password, status_code", [
    (None, 'Password123$', 422),
    ('user@example.com', None, 422),
    ('user@example.com', "Password123$", 201),
    ('user@example.com', "password123$", 422),
    ('user@example.com', "Password123", 422),
    ('user@example.com', "Passwordabc$", 422),
    ('user@example.com', "Pad123$", 422),
])
def test_create_user(client,email, password, status_code):
    res = client.post(
        "/user/signup", json={"email": email, "password": password})
    assert res.status_code == status_code
