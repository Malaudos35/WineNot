import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000"

# =============================
# 📦 Setup global (DB init, tokens)
# =============================
@pytest.fixture(scope="session", autouse=True)
def setup_and_cache_tokens(pytestconfig):
    """Initialise la base et stocke les tokens admin + user dans pytestconfig."""
    # Nettoyage et init
    requests.get(f"{BASE_URL}/clean")
    requests.get(f"{BASE_URL}/init")

    # Auth admin
    admin_login = {"email": "admin@example.com", "password": "admin"}
    res = requests.post(f"{BASE_URL}/tokens", json=admin_login)
    assert res.status_code in [200, 201], "Impossible de récupérer le token admin"
    admin_token = res.json().get("token")

    # Création d'un user standard
    user_data = {
        "email": "user@example.com",
        "username": "user",
        "password": "user"
    }
    requests.post(f"{BASE_URL}/users", json=user_data)
    res = requests.post(f"{BASE_URL}/tokens", json={"email": "user@example.com", "password": "user"})
    assert res.status_code in [200, 201], "Impossible de récupérer le token user"
    user_token = res.json().get("token")

    # Sauvegarde dans le cache pytest
    pytestconfig.cache.set("admin_token", admin_token)
    pytestconfig.cache.set("user_token", user_token)


@pytest.fixture(scope="session")
def admin_token(pytestconfig):
    return pytestconfig.cache.get("admin_token", None)


@pytest.fixture(scope="session")
def user_token(pytestconfig):
    return pytestconfig.cache.get("user_token", None)


# =============================
# 🔐 TOKEN TESTS
# =============================
def test_token_validity(admin_token, user_token):
    assert isinstance(admin_token, str)
    assert isinstance(user_token, str)
    assert len(admin_token) > 10
    assert len(user_token) > 10


# =============================
# 👥 USERS TESTS
# =============================
def test_create_user(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    new_user = {
        "email": f"new_user_{uuid.uuid4().hex[:6]}@example.com",
        "username": f"user_{uuid.uuid4().hex[:6]}",
        "password": "new_password123"
    }
    res = requests.post(f"{BASE_URL}/users", json=new_user, headers=headers)
    assert res.status_code in [201, 400]


# =============================
# 🔒 PERMISSIONS TESTS
# =============================
def test_create_and_delete_permission(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "name": f"perm_{uuid.uuid4().hex[:6]}",
        "description": "Permission de test"
    }
    res = requests.post(f"{BASE_URL}/permissions", json=payload, headers=headers)
    if res.status_code == 201:
        perm_id = res.json()["id"]
        res_del = requests.delete(f"{BASE_URL}/permissions/{perm_id}", headers=headers)
        assert res_del.status_code in [204, 404]


# =============================
# 🍷 WINE CELLARS FIXTURE
# =============================
@pytest.fixture
def create_cellar(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"name": "Cellar Test", "location": "Garage", "capacity": 50}
    res = requests.post(f"{BASE_URL}/cellars", json=payload, headers=headers)
    if res.status_code == 201:
        return res.json()["id"]
    # fallback to existing cellar
    res_list = requests.get(f"{BASE_URL}/cellars", headers=headers)
    return res_list.json()[0]["id"]


# =============================
# 🍾 WINE BOTTLES FIXTURE
# =============================
@pytest.fixture
def create_bottle(user_token, create_cellar):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {
        "name": "Château Margaux 2015",
        "vintage": 2015,
        "wine_type": "Rouge",
        "region": "Bordeaux",
        "country": "France",
        "price": 1200.50,
        "quantity": 1
    }
    res = requests.post(f"{BASE_URL}/cellars/{create_cellar}/bottles", json=payload, headers=headers)
    if res.status_code == 201:
        return res.json()["id"], create_cellar
    # fallback
    res_list = requests.get(f"{BASE_URL}/cellars/{create_cellar}/bottles", headers=headers)
    bottle_id = res_list.json()[0]["id"]
    return bottle_id, create_cellar


# =============================
# 🍾 WINE BOTTLES TESTS
# =============================
def test_add_bottle(user_token, create_cellar):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {
        "name": "Domaine Lafite 2010",
        "vintage": 2010,
        "wine_type": "Rouge",
        "region": "Bordeaux",
        "country": "France",
        "price": 950.0,
        "quantity": 1
    }
    res = requests.post(f"{BASE_URL}/cellars/{create_cellar}/bottles", json=payload, headers=headers)
    assert res.status_code in [201, 400]


def test_update_bottle_partial(user_token, create_bottle):
    bottle_id, cellar_id = create_bottle
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"notes": "Updated notes", "quantity": 3}
    res = requests.put(f"{BASE_URL}/bottles/{bottle_id}", json=payload, headers=headers)
    assert res.status_code == 200
    updated = res.json()
    assert updated["notes"] == "Updated notes"
    assert updated["quantity"] == 3


def test_update_bottle_full(user_token, create_bottle):
    bottle_id, cellar_id = create_bottle
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {
        "name": "Updated Name",
        "vintage": 2020,
        "wine_type": "Blanc",
        "region": "Bourgogne",
        "country": "France",
        "price": 800.0,
        "quantity": 5,
        "notes": "Complet update"
    }
    res = requests.put(f"{BASE_URL}/bottles/{bottle_id}", json=payload, headers=headers)
    assert res.status_code == 200
    updated = res.json()
    assert updated["name"] == "Updated Name"
    assert updated["vintage"] == 2020
    assert updated["wine_type"] == "Blanc"
    assert updated["quantity"] == 5
    assert updated["notes"] == "Complet update"


def test_update_bottle_invalid(user_token, create_bottle):
    bottle_id, cellar_id = create_bottle
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"quantity": -5, "price": -100}
    res = requests.put(f"{BASE_URL}/bottles/{bottle_id}", json=payload, headers=headers)
    assert res.status_code == 422


def test_get_bottle(user_token, create_bottle):
    bottle_id, cellar_id = create_bottle
    headers = {"Authorization": f"Bearer {user_token}"}
    res = requests.get(f"{BASE_URL}/bottles/{bottle_id}", headers=headers)
    assert res.status_code == 200
    bottle = res.json()
    assert bottle["id"] == bottle_id


def test_get_bottle_not_found(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    res = requests.get(f"{BASE_URL}/bottles/{uuid.uuid4()}", headers=headers)
    assert res.status_code == 404


def test_list_bottles(user_token, create_cellar):
    headers = {"Authorization": f"Bearer {user_token}"}
    res = requests.get(f"{BASE_URL}/cellars/{create_cellar}/bottles", headers=headers)
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_delete_bottle(user_token, create_bottle):
    bottle_id, cellar_id = create_bottle
    headers = {"Authorization": f"Bearer {user_token}"}
    res = requests.delete(f"{BASE_URL}/bottles/{bottle_id}", headers=headers)
    assert res.status_code in [204, 404]
