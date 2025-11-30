import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000/api"


#
# ============================
# 🔧 HELPERS
# ============================
#

def api(method, path, token=None, **kwargs):
    headers = {}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return requests.request(method, f"{BASE_URL}{path}", headers=headers, **kwargs)


#
# ============================
# 🧹 INIT GLOBAL
# ============================
#

@pytest.fixture(scope="session", autouse=True)
def setup_db(pytestconfig):

    # Reset complet
    requests.get(f"{BASE_URL}/clean")
    requests.get(f"{BASE_URL}/init")

    #
    # Admin
    #
    admin_login = {"email": "admin@example.com", "password": "admin"}
    res = api("post", "/tokens", json=admin_login)
    assert res.status_code in (200, 201)
    admin_token = res.json()["token"]

    #
    # User standard
    #
    user_email = f"user_{uuid.uuid4().hex[:5]}@example.com"
    user_data = {"email": user_email, "username": "user", "password": "user"}

    api("post", "/users", json=user_data, token=admin_token)

    res_u = api("post", "/tokens", json={"email": user_email, "password": "user"})
    user_token = res_u.json()["token"]

    pytestconfig.cache.set("admin_token", admin_token)
    pytestconfig.cache.set("user_token", user_token)


@pytest.fixture(scope="session")
def admin_token(pytestconfig):
    return pytestconfig.cache.get("admin_token", None)


@pytest.fixture(scope="session")
def user_token(pytestconfig):
    return pytestconfig.cache.get("user_token", None)


#
# ============================
# 🔧 Factories réutilisables
# ============================
#

@pytest.fixture
def create_user(admin_token):
    def _create_user():
        email = f"user_{uuid.uuid4().hex[:6]}@example.com"
        payload = {"email": email, "username": "u"+uuid.uuid4().hex[:4], "password": "pass"}
        res = api("post", "/users", json=payload, token=admin_token)
        assert res.status_code in (201, 400)
        if res.status_code == 201:
            return res.json()
    return _create_user


@pytest.fixture
def create_cellar(user_token):
    def _create_cellar():
        payload = {
            "name": f"Cellar {uuid.uuid4().hex[:5]}",
            "location": "Test",
            "capacity": 100
        }
        res = api("post", "/cellars", json=payload, token=user_token)
        assert res.status_code in (201, 400)
        if res.status_code == 201:
            return res.json()
    return _create_cellar


@pytest.fixture
def create_bottle(user_token, create_cellar):
    def _create_bottle():
        cellar = create_cellar()
        if not cellar:
            return None

        payload = {
            "name": "Test Wine",
            "vintage": 2000,
            "wine_type": "Rouge",
            "region": "Bordeaux",
            "country": "France",
            "price": 50.0,
            "quantity": 1
        }
        res = api("post", f"/cellars/{cellar['id']}/bottles",
                  json=payload, token=user_token)
        assert res.status_code in (201, 400)
        if res.status_code == 201:
            return cellar["id"], res.json()
    return _create_bottle
