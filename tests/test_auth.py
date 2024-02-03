def test_login_user(test_user, client):
    with client:
        response = client.post("/login", data={"username": test_user['email'], "password": test_user['password']})
        res=response.json()
        
        assert res["token_type"] == "bearer"
        assert response.status_code == 200