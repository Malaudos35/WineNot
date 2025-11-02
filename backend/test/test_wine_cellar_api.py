import pytest
import requests

# ---------------------------
# Fixtures
# ---------------------------

@pytest.fixture(scope="session")
def base_url():
    return "http://localhost:5000"

@pytest.fixture(scope="session", autouse=True)
def clean_database(base_url):
    """Nettoyer la base avant les tests"""
    response = requests.post(f"{base_url}/clean")
    assert response.status_code == 200
    yield

@pytest.fixture(scope="session")
def user_token(base_url):
    # Création utilisateur pour les tests
    response = requests.post(
        f"{base_url}/users",
        json={
            "email": "test_user@example.com",
            "username": "test_user",
            "password": "admin"
        }
    )
    assert response.status_code == 201
    # Récupération token
    res = requests.post(
        f"{base_url}/tokens",
        json={"email": "test_user@example.com", "password": "password123"}
    )
    assert res.status_code == 201
    return res.json()["token"]

@pytest.fixture(scope="session")
def admin_token(base_url):
    # Création admin pour tests permissions
    response = requests.post(
        f"{base_url}/users",
        json={
            "email": "admin@example.com",
            "username": "admin",
            "password": "adminpass",
            "is_admin": True
        }
    )
    assert response.status_code == 201
    res = requests.post(
        f"{base_url}/tokens",
        json={"email": "admin@example.com", "password": "adminpass"}
    )
    assert res.status_code == 201
    return res.json()["token"]

# ---------------------------
# Tests Auth / Users
# ---------------------------

def test_generate_token(base_url, user_token):
    # user_token fixture génère déjà le token
    assert len(user_token) > 0

def test_create_user_duplicate(base_url):
    # Essaie de créer un utilisateur déjà existant
    response = requests.post(
        f"{base_url}/users",
        json={"email": "test_user@example.com", "username": "test_user", "password": "password123"}
    )
    assert response.status_code == 400

def test_invalid_login(base_url):
    response = requests.post(
        f"{base_url}/tokens",
        json={"email": "wrong@example.com", "password": "wrongpass"}
    )
    assert response.status_code == 401

# ---------------------------
# Tests Permissions
# ---------------------------

def test_list_permissions(base_url, admin_token):
    headers = {"Authorization": f"Bearer {admin_token}"}
    response = requests.get(f"{base_url}/permissions", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ---------------------------
# Tests Wine Cellars
# ---------------------------

def test_create_wine_cellar(base_url, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.post(
        f"{base_url}/wine-cellars",
        headers=headers,
        json={"name": "Ma Cave", "location": "Sous-sol", "capacity": 100}
    )
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    # Retourner l'id pour tests suivants
    return data["id"]

def test_get_wine_cellars(base_url, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{base_url}/wine-cellars", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# ---------------------------
# Tests Wine Bottles
# ---------------------------

def test_add_wine_bottle(base_url, user_token):
    # D'abord créer une cave
    headers = {"Authorization": f"Bearer {user_token}"}
    cellar_resp = requests.post(
        f"{base_url}/wine-cellars",
        headers=headers,
        json={"name": "Cave pour bouteilles", "location": "Garage", "capacity": 50}
    )
    cellar_id = cellar_resp.json()["id"]

    # Ajouter une bouteille
    bottle_resp = requests.post(
        f"{base_url}/wine-bottles",
        headers=headers,
        json={
            "cellar_id": cellar_id,
            "name": "Château Margaux 2015",
            "vintage": 2015,
            "wine_type": "Rouge",
            "region": "Bordeaux",
            "country": "France",
            "price": 1200.5,
            "quantity": 1,
            "notes": "Grand cru classé",
            "image_url": "https://example.com/margaux.jpg"
        }
    )
    assert bottle_resp.status_code == 201
    data = bottle_resp.json()
    assert "id" in data
    return data["id"]

def test_list_wine_bottles(base_url, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    response = requests.get(f"{base_url}/wine-bottles", headers=headers)
    assert response.status_code == 200
    assert isinstance(response.json(), list)

def test_delete_wine_bottle(base_url, user_token):
    headers = {"Authorization": f"Bearer {user_token}"}
    # Crée une cave et bouteille
    cellar_resp = requests.post(
        f"{base_url}/wine-cellars",
        headers=headers,
        json={"name": "Cave à détruire", "location": "Garage", "capacity": 10}
    )
    cellar_id = cellar_resp.json()["id"]

    bottle_resp = requests.post(
        f"{base_url}/wine-bottles",
        headers=headers,
        json={
            "cellar_id": cellar_id,
            "name": "Bouteille temporaire",
            "vintage": 2020,
            "wine_type": "Rouge",
            "region": "Bordeaux",
            "country": "France",
            "price": 50,
            "quantity": 1,
            "notes": "",
            "image_url": "https://example.com/tmp.jpg"
        }
    )
    bottle_id = bottle_resp.json()["id"]

    # Suppression
    del_resp = requests.delete(f"{base_url}/wine-bottles/{bottle_id}", headers=headers)
    assert del_resp.status_code == 200

# ---------------------------
# Tests Clean
# ---------------------------

def test_clean_database_route(base_url):
    response = requests.post(f"{base_url}/clean")
    assert response.status_code == 200
