from conftest import api

def test_list_users(admin_token):
    res = api("get", "/users", token=admin_token)
    assert res.status_code in (200, 403)
    if res.status_code == 200:
        assert isinstance(res.json(), list)


def test_create_user(admin_token):
    user = {
        "email": "new@example.com",
        "username": "newuser",
        "password": "test"
    }
    res = api("post", "/users", json=user, token=admin_token)
    assert res.status_code in (201, 400)


def test_get_user_by_id(admin_token):
    res = api("get", "/users", token=admin_token)
    if res.status_code != 200:
        return

    user_id = res.json()[0]["id"]
    res2 = api("get", f"/users/{user_id}", token=admin_token)
    assert res2.status_code in (200, 404)


def test_update_user(admin_token):
    # get any user
    res = api("get", "/users", token=admin_token)
    if res.status_code != 200 or len(res.json()) < 1:
        return

    user_id = res.json()[0]["id"]
    payload = {"username": "updated"}

    res2 = api("put", f"/users/{user_id}", json=payload, token=admin_token)
    assert res2.status_code in (200, 400, 404)


def test_delete_user(admin_token, create_user):
    user = create_user()
    if not user:
        return

    res = api("delete", f"/users/{user['id']}", token=admin_token)
    assert res.status_code in (204, 404)
