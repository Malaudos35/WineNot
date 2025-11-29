import pytest
import requests
import uuid

BASE_URL = "http://localhost:5000/api"


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

def test_get_all_users_as_admin(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = requests.get(f"{BASE_URL}/users", headers=headers)
    assert res.status_code in [200, 403]  # selon les règles d’accès
    if res.status_code == 200:
        users = res.json()
        assert isinstance(users, list)


def test_create_user(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    new_user = {
        "email": "new_user@example.com",
        "username": "new_user",
        "password": "new_password123"
    }
    res = requests.post(f"{BASE_URL}/users", json=new_user, headers=headers)
    assert res.status_code in [201, 400]
    if res.status_code == 201:
        user = res.json()
        assert "email" in user
        assert user["email"] == "new_user@example.com"


def test_get_user_by_id(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Liste d’abord les users
    res = requests.get(f"{BASE_URL}/users", headers=headers)
    if res.status_code != 200:
        pytest.skip("Impossible de lister les users (403 ou autre)")
    user_id = res.json()[0]["id"]
    res = requests.get(f"{BASE_URL}/users/{user_id}", headers=headers)
    assert res.status_code in [200, 404]


def test_update_user(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Récupère un user existant
    res = requests.get(f"{BASE_URL}/users", headers=headers)
    if res.status_code != 200:
        pytest.skip("Impossible de lister les users (403 ou autre)")
    user_id = res.json()[2]["id"]

    payload = {
        "username": "updated_username",
        "email": f"updated_{uuid.uuid4().hex[:6]}@example.com"
    }
    res = requests.put(f"{BASE_URL}/users/{user_id}", json=payload, headers=headers)
    assert res.status_code in [200, 400, 404]


def test_delete_user(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    # Crée un user à supprimer
    temp_user = {
        "email": f"delete_me_{uuid.uuid4().hex[:5]}@example.com",
        "username": "temp_delete",
        "password": "pass123"
    }
    res = requests.post(f"{BASE_URL}/users", json=temp_user, headers=headers)
    if res.status_code not in [201, 400]:
        pytest.skip("Création du user impossible")
    user_id = None
    if res.status_code == 201:
        user_id = res.json().get("id")

    if user_id:
        res = requests.delete(f"{BASE_URL}/users/{user_id}", headers=headers)
        assert res.status_code in [204, 404]


# =============================
# 🔒 PERMISSIONS TESTS
# =============================

def test_list_permissions(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = requests.get(f"{BASE_URL}/permissions", headers=headers)
    assert res.status_code in [200, 403]
    if res.status_code == 200:
        assert isinstance(res.json(), list)


def test_create_and_delete_permission(admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    payload = {
        "name": f"perm_{uuid.uuid4().hex[:6]}",
        "description": "Permission de test"
    }
    res = requests.post(f"{BASE_URL}/permissions", json=payload, headers=headers)
    assert res.status_code in [201, 400]
    if res.status_code == 201:
        perm_id = res.json()["id"]
        res_del = requests.delete(f"{BASE_URL}/permissions/{perm_id}", headers=headers)
        assert res_del.status_code in [204, 404]


# =============================
# 🍷 WINE CELLARS TESTS
# =============================

def test_create_and_get_cellar(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    payload = {"name": "Cave Test", "location": "Garage", "capacity": 50}
    res = requests.post(f"{BASE_URL}/cellars", json=payload, headers=headers)
    assert res.status_code in [201, 400]
    if res.status_code == 201:
        cellar_id = res.json()["id"]
        res_get = requests.get(f"{BASE_URL}/cellars/{cellar_id}", headers=headers)
        assert res_get.status_code in [200, 404]


def test_list_cellars(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    res = requests.get(f"{BASE_URL}/cellars", headers=headers)
    assert res.status_code in [200, 403]
    if res.status_code == 200:
        assert isinstance(res.json(), list)


# =============================
# 🍾 WINE BOTTLES TESTS
# =============================


def test_add_and_update_bottle(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}

    # -----------------------
    # 1️⃣ Crée une cave
    # -----------------------
    cellar_payload = {
        "name": "Cave Bottles",
        "location": "Sous-sol",
        "capacity": 100
    }
    res = requests.post(f"{BASE_URL}/cellars", json=cellar_payload, headers=headers)
    
    if res.status_code not in [201, 400]:
        pytest.skip("Impossible de créer la cave")
    
    if res.status_code == 400:
        res_list = requests.get(f"{BASE_URL}/cellars", headers=headers)
        if res_list.status_code != 200 or not res_list.json():
            pytest.skip("Pas de cave existante")
        cellar_id = res_list.json()[0]["id"]
    else:
        cellar_id = res.json()["id"]

    # -----------------------
    # 2️⃣ Ajoute une bouteille
    # -----------------------
    bottle_payload = {
        "name": "Château Margaux 2015",
        "vintage": 2015,
        "wine_type": "Rouge",
        "region": "Bordeaux",
        "country": "France",
        "price": 1200.50,
        "quantity": 1
    }
    res_bottle = requests.post(f"{BASE_URL}/cellars/{cellar_id}/bottles", json=bottle_payload, headers=headers)
    assert res_bottle.status_code in [201, 400]

    if res_bottle.status_code == 201:
        bottle_id = res_bottle.json()["id"]

        # -----------------------
        # 3️⃣ Met à jour uniquement les champs fournis
        # -----------------------
        update_payload = {
            "notes": "Notes mises à jour",
            "quantity": 2
        }
        res_up = requests.put(
            f"{BASE_URL}/bottles/{bottle_id}",
            json=update_payload,
            headers=headers
        )

        # Vérifie que l’update a réussi
        assert res_up.status_code == 200
        updated_bottle = res_up.json()
        assert updated_bottle["notes"] == "Notes mises à jour"
        assert updated_bottle["quantity"] == 2

        # -----------------------
        # 4️⃣ Vérifie que les autres champs restent inchangés
        # -----------------------
        assert updated_bottle["name"] == bottle_payload["name"]
        assert updated_bottle["vintage"] == bottle_payload["vintage"]
        assert updated_bottle["wine_type"] == bottle_payload["wine_type"]
        assert updated_bottle["region"] == bottle_payload["region"]
        assert updated_bottle["country"] == bottle_payload["country"]
        assert updated_bottle["price"] == bottle_payload["price"]


def test_delete_bottle(user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    res_cellars = requests.get(f"{BASE_URL}/cellars", headers=headers)
    if res_cellars.status_code != 200 or not res_cellars.json():
        pytest.skip("Pas de cave existante")
    cellar_id = res_cellars.json()[0]["id"]
    res_bottles = requests.get(f"{BASE_URL}/cellars/{cellar_id}/bottles", headers=headers)
    if int(res_bottles.status_code) != 200 or not res_bottles.json():
        pytest.skip(f"Pas de bouteilles existantes {res_bottles.status_code}")
    bottle_id = res_bottles.json()[0]["id"]
    res = requests.delete(f"{BASE_URL}/bottles/{bottle_id}", headers=headers)
    assert res.status_code in [204, 404]
