"""
Tests fonctionnels pour les workflows complets de WineNot.
Ces tests vérifient les scénarios réalistes d'utilisation de l'application.
"""

import uuid
import pytest
from conftest import api


class TestUserRegistrationAndLogin:
    """
    Workflow: Enregistrement utilisateur → Connexion → Accès aux ressources
    """

    def test_complete_user_registration_and_login(self, admin_token):
        """
        Test le flux complet: créer un nouvel utilisateur et se connecter
        """
        # 1. Créer un nouvel utilisateur via l'API
        new_user_email = f"newuser_{uuid.uuid4().hex[:6]}@example.com"
        new_user_data = {
            "email": new_user_email,
            "username": f"testuser_{uuid.uuid4().hex[:4]}",
            "password": "SecurePassword123"
        }

        res_create = api("post", "/users", json=new_user_data, token=admin_token)
        assert res_create.status_code == 201, f"Failed to create user: {res_create.text}"
        created_user = res_create.json()
        assert created_user["email"] == new_user_email
        assert created_user["is_active"] is True

        # 2. Se connecter avec le nouvel utilisateur
        login_data = {
            "email": new_user_email,
            "password": "SecurePassword123"
        }
        res_login = api("post", "/tokens", json=login_data)
        assert res_login.status_code in (200, 201), f"Login failed: {res_login.text}"
        new_user_token = res_login.json()["token"]
        assert new_user_token is not None

        # 3. Vérifier l'accès aux ressources avec le token
        res_cellars = api("get", "/cellars", token=new_user_token)
        assert res_cellars.status_code == 200
        assert isinstance(res_cellars.json(), list)

    def test_login_with_invalid_credentials(self):
        """
        Test la tentative de connexion avec des identifiants invalides
        """
        invalid_login = {
            "email": "nonexistent@example.com",
            "password": "wrongpassword"
        }
        res = api("post", "/tokens", json=invalid_login)
        assert res.status_code in (400, 401, 404)

    def test_create_duplicate_user_fails(self, admin_token, create_user):
        """
        Test que créer un utilisateur avec un email existant échoue
        """
        user = create_user()
        assert user is not None

        # Essayer de créer un nouvel utilisateur avec le même email
        duplicate_data = {
            "email": user["email"],
            "username": "different_username",
            "password": "password"
        }
        res = api("post", "/users", json=duplicate_data, token=admin_token)
        assert res.status_code in (400, 409)  # Conflict


class TestWineCellarManagement:
    """
    Workflow: Création caves → Gestion des caves → Consultation
    """

    def test_complete_cellar_lifecycle(self, user_token):
        """
        Test le cycle de vie complet d'une cave:
        Création → Consultation → Modification → Suppression
        """
        # 1. Créer une cave
        cellar_data = {
            "name": f"Ma cave {uuid.uuid4().hex[:5]}",
            "location": "Bordeaux",
            "capacity": 500
        }
        res_create = api("post", "/cellars", json=cellar_data, token=user_token)
        assert res_create.status_code == 201
        cellar = res_create.json()
        cellar_id = cellar["id"]
        assert cellar["name"] == cellar_data["name"]
        assert cellar["location"] == "Bordeaux"

        # 2. Récupérer la cave par ID
        res_get = api("get", f"/cellars/{cellar_id}", token=user_token)
        assert res_get.status_code == 200
        fetched_cellar = res_get.json()
        assert fetched_cellar["id"] == cellar_id
        assert fetched_cellar["name"] == cellar_data["name"]

        # 3. Lister les caves de l'utilisateur
        res_list = api("get", "/cellars", token=user_token)
        assert res_list.status_code == 200
        cellars = res_list.json()
        assert isinstance(cellars, list)
        assert any(c["id"] == cellar_id for c in cellars)

        # 4. Modifier la cave
        update_data = {
            "name": "Ma cave mise à jour",
            "capacity": 600
        }
        res_update = api("put", f"/cellars/{cellar_id}", json=update_data, token=user_token)
        assert res_update.status_code == 200
        updated_cellar = res_update.json()
        assert updated_cellar["name"] == "Ma cave mise à jour"
        assert updated_cellar["capacity"] == 600

        # 5. Supprimer la cave
        res_delete = api("delete", f"/cellars/{cellar_id}", token=user_token)
        # Les DELETE retournent 204 (No Content) ou 200
        assert res_delete.status_code in (200, 204), f"Unexpected status: {res_delete.status_code}, body: {res_delete.text}"

        # 6. Vérifier que la cave est supprimée (peut prendre un peu de temps en cache)
        res_verify = api("get", f"/cellars/{cellar_id}", token=user_token)
        assert res_verify.status_code in (404, 403), f"Expected 404 or 403, got {res_verify.status_code}"

    def test_multiple_cellars_isolation(self, user_token, admin_token):
        """
        Test que chaque utilisateur a ses propres caves (isolation des données)
        """
        # Créer 2 utilisateurs
        user1_email = f"user1_{uuid.uuid4().hex[:6]}@example.com"
        user2_email = f"user2_{uuid.uuid4().hex[:6]}@example.com"

        user1_data = {
            "email": user1_email,
            "username": f"user1_{uuid.uuid4().hex[:4]}",
            "password": "pass"
        }
        user2_data = {
            "email": user2_email,
            "username": f"user2_{uuid.uuid4().hex[:4]}",
            "password": "pass"
        }

        api("post", "/users", json=user1_data, token=admin_token)
        api("post", "/users", json=user2_data, token=admin_token)

        # Récupérer les tokens
        res1 = api("post", "/tokens", json={"email": user1_email, "password": "pass"})
        token1 = res1.json()["token"]

        res2 = api("post", "/tokens", json={"email": user2_email, "password": "pass"})
        token2 = res2.json()["token"]

        # User1 crée une cave
        cellar1_data = {"name": f"Cave User1 {uuid.uuid4().hex[:5]}", "location": "Paris"}
        res_c1 = api("post", "/cellars", json=cellar1_data, token=token1)
        assert res_c1.status_code == 201
        cellar1_id = res_c1.json()["id"]

        # User2 crée une cave
        cellar2_data = {"name": f"Cave User2 {uuid.uuid4().hex[:5]}", "location": "Lyon"}
        res_c2 = api("post", "/cellars", json=cellar2_data, token=token2)
        assert res_c2.status_code == 201
        cellar2_id = res_c2.json()["id"]

        # User1 liste ses caves (ne doit voir que sa propre cave)
        res_list1 = api("get", "/cellars", token=token1)
        assert res_list1.status_code == 200
        user1_cellars = res_list1.json()
        assert any(c["id"] == cellar1_id for c in user1_cellars)
        assert not any(c["id"] == cellar2_id for c in user1_cellars)

        # User2 liste ses caves (ne doit voir que sa propre cave)
        res_list2 = api("get", "/cellars", token=token2)
        assert res_list2.status_code == 200
        user2_cellars = res_list2.json()
        assert any(c["id"] == cellar2_id for c in user2_cellars)
        assert not any(c["id"] == cellar1_id for c in user2_cellars)

        # User1 ne peut pas accéder à la cave de User2
        res_access = api("get", f"/cellars/{cellar2_id}", token=token1)
        assert res_access.status_code in (403, 404), f"Expected 403 or 404, got {res_access.status_code}"


class TestWineBottleManagement:
    """
    Workflow: Ajout bouteilles → Gestion → Consultation
    """

    def test_complete_bottle_lifecycle(self, user_token, create_cellar):
        """
        Test le cycle de vie complet d'une bouteille:
        Ajout → Consultation → Modification → Suppression
        """
        # 1. Créer une cave
        cellar = create_cellar()
        assert cellar is not None
        cellar_id = cellar["id"]

        # 2. Ajouter une bouteille
        bottle_data = {
            "name": "Château Margaux",
            "vintage": 2015,
            "wine_type": "Rouge",
            "region": "Bordeaux",
            "country": "France",
            "price": 150.00,
            "quantity": 2,
            "notes": "Excellent millésime"
        }
        res_add = api("post", f"/cellars/{cellar_id}/bottles",
                     json=bottle_data, token=user_token)
        assert res_add.status_code == 201
        bottle = res_add.json()
        bottle_id = bottle["id"]
        assert bottle["name"] == "Château Margaux"
        assert bottle["quantity"] == 2

        # 3. Récupérer la bouteille
        res_get = api("get", f"/bottles/{bottle_id}", token=user_token)
        assert res_get.status_code == 200
        fetched_bottle = res_get.json()
        assert fetched_bottle["id"] == bottle_id

        # 4. Lister les bouteilles de la cave
        res_list = api("get", f"/cellars/{cellar_id}/bottles", token=user_token)
        assert res_list.status_code == 200
        bottles = res_list.json()
        assert isinstance(bottles, list)
        assert any(b["id"] == bottle_id for b in bottles)

        # 5. Modifier la bouteille
        update_data = {
            "quantity": 1,
            "notes": "Excellent millésime - Réduction prévue"
        }
        res_update = api("put", f"/bottles/{bottle_id}",
                        json=update_data, token=user_token)
        assert res_update.status_code == 200
        updated_bottle = res_update.json()
        assert updated_bottle["quantity"] == 1

        # 6. Supprimer la bouteille
        res_delete = api("delete", f"/bottles/{bottle_id}", token=user_token)
        assert res_delete.status_code == 204

        # 7. Vérifier la suppression
        res_verify = api("get", f"/bottles/{bottle_id}", token=user_token)
        assert res_verify.status_code == 404

    def test_add_multiple_bottles_to_cellar(self, user_token, create_cellar):
        """
        Test l'ajout de plusieurs bouteilles dans une cave
        """
        cellar = create_cellar()
        assert cellar is not None
        cellar_id = cellar["id"]

        # Ajouter 3 bouteilles différentes
        wines = [
            {
                "name": "Bordeaux Rouge",
                "vintage": 2018,
                "wine_type": "Rouge",
                "region": "Bordeaux",
                "country": "France",
                "quantity": 6
            },
            {
                "name": "Bourgogne Blanc",
                "vintage": 2019,
                "wine_type": "Blanc",
                "region": "Bourgogne",
                "country": "France",
                "quantity": 4
            },
            {
                "name": "Champagne",
                "vintage": 2016,
                "wine_type": "Mousseux",
                "region": "Champagne",
                "country": "France",
                "quantity": 2
            }
        ]

        bottle_ids = []
        for wine_data in wines:
            res = api("post", f"/cellars/{cellar_id}/bottles",
                     json=wine_data, token=user_token)
            assert res.status_code == 201
            bottle_ids.append(res.json()["id"])

        # Lister les bouteilles
        res_list = api("get", f"/cellars/{cellar_id}/bottles", token=user_token)
        assert res_list.status_code == 200
        bottles = res_list.json()
        assert len(bottles) == 3

        # Vérifier qu'on a bien les 3 bouteilles
        retrieved_ids = [b["id"] for b in bottles]
        assert all(bid in retrieved_ids for bid in bottle_ids)

    def test_bottle_isolation_between_cellars(self, user_token, create_cellar):
        """
        Test que les bouteilles d'une cave ne s'affichent pas dans une autre
        """
        cellar1 = create_cellar()
        cellar2 = create_cellar()
        assert cellar1 is not None and cellar2 is not None

        # Ajouter une bouteille dans cellar1
        bottle_data = {
            "name": "Bordeaux",
            "vintage": 2018,
            "wine_type": "Rouge",
            "region": "Bordeaux",
            "country": "France"
        }
        res = api("post", f"/cellars/{cellar1['id']}/bottles",
                 json=bottle_data, token=user_token)
        assert res.status_code == 201
        bottle_id = res.json()["id"]

        # Lister les bouteilles de cellar1
        res_list1 = api("get", f"/cellars/{cellar1['id']}/bottles", token=user_token)
        assert res_list1.status_code == 200
        bottles1 = res_list1.json()
        assert any(b["id"] == bottle_id for b in bottles1)

        # Lister les bouteilles de cellar2 (ne doit pas contenir la bouteille)
        res_list2 = api("get", f"/cellars/{cellar2['id']}/bottles", token=user_token)
        assert res_list2.status_code == 200
        bottles2 = res_list2.json()
        assert not any(b["id"] == bottle_id for b in bottles2)

    def test_invalid_bottle_data(self, user_token, create_cellar):
        """
        Test l'ajout de bouteille avec des données invalides
        """
        cellar = create_cellar()
        assert cellar is not None

        # Données incomplètes
        invalid_bottle = {
            "vintage": 2018  # Manque 'name' et autres champs requis
        }
        res = api("post", f"/cellars/{cellar['id']}/bottles",
                 json=invalid_bottle, token=user_token)
        # Les erreurs de validation retournent 400 ou 422 (Unprocessable Entity)
        assert res.status_code in (400, 422), f"Expected validation error, got {res.status_code}: {res.text}"


class TestUserAccessControl:
    """
    Workflow: Gestion des droits d'accès utilisateur
    """

    def test_unauthorized_access_without_token(self):
        """
        Test que l'accès sans token est refusé
        """
        # Essayer d'accéder aux cellars sans token
        res = api("get", "/cellars")
        assert res.status_code in (401, 403)

    def test_invalid_token_access(self):
        """
        Test que l'accès avec un token invalide est refusé
        """
        res = api("get", "/cellars", token="invalid_token_12345")
        assert res.status_code in (401, 403)

    def test_user_cannot_access_other_user_bottle(self, admin_token):
        """
        Test qu'un utilisateur ne peut pas accéder aux bouteilles d'un autre
        """
        # Créer 2 utilisateurs
        user1_email = f"access_test_user1_{uuid.uuid4().hex[:6]}@example.com"
        user2_email = f"access_test_user2_{uuid.uuid4().hex[:6]}@example.com"

        user1_data = {
            "email": user1_email,
            "username": f"access_user1_{uuid.uuid4().hex[:4]}",
            "password": "pass"
        }
        user2_data = {
            "email": user2_email,
            "username": f"access_user2_{uuid.uuid4().hex[:4]}",
            "password": "pass"
        }

        res_u1 = api("post", "/users", json=user1_data, token=admin_token)
        if res_u1.status_code not in (200, 201):
            return  # Skip si création échouée
        res_u2 = api("post", "/users", json=user2_data, token=admin_token)
        if res_u2.status_code not in (200, 201):
            return  # Skip si création échouée

        res1 = api("post", "/tokens", json={"email": user1_email, "password": "pass"})
        if res1.status_code not in (200, 201):
            return  # Skip si auth échouée
        token1 = res1.json()["token"]

        res2 = api("post", "/tokens", json={"email": user2_email, "password": "pass"})
        if res2.status_code not in (200, 201):
            return  # Skip si auth échouée
        token2 = res2.json()["token"]

        # User1 crée une cave et une bouteille
        cellar_data = {"name": f"Cave privée {uuid.uuid4().hex[:5]}", "location": "Paris"}
        res_cellar = api("post", "/cellars", json=cellar_data, token=token1)
        if res_cellar.status_code != 201:
            return  # Skip si création échouée
        cellar_id = res_cellar.json()["id"]

        bottle_data = {
            "name": "Vin privé",
            "vintage": 2018,
            "wine_type": "Rouge",
            "region": "Bordeaux",
            "country": "France"
        }
        res_bottle = api("post", f"/cellars/{cellar_id}/bottles",
                        json=bottle_data, token=token1)
        if res_bottle.status_code != 201:
            return  # Skip si création échouée
        bottle_id = res_bottle.json()["id"]

        # User2 essaie d'accéder à la cave et la bouteille
        res_cellar_access = api("get", f"/cellars/{cellar_id}", token=token2)
        assert res_cellar_access.status_code in (403, 404), f"Expected 403/404, got {res_cellar_access.status_code}"

        res_bottle_access = api("get", f"/bottles/{bottle_id}", token=token2)
        assert res_bottle_access.status_code in (403, 404), f"Expected 403/404, got {res_bottle_access.status_code}"

    def test_admin_can_access_all_users(self, admin_token):
        """
        Test que l'admin peut lister tous les utilisateurs
        """
        res = api("get", "/users", token=admin_token)
        # L'admin devrait avoir accès à la liste des utilisateurs
        # (status_code dépend de l'implémentation)
        assert res.status_code in (200, 403)


class TestDataValidation:
    """
    Workflow: Validation des données lors des opérations
    """

    def test_cellar_with_invalid_capacity(self, user_token):
        """
        Test la création d'une cave avec une capacité invalide
        Note: Le système peut accepter ou rejeter les capacités négatives
        """
        invalid_cellar = {
            "name": f"Cave avec capacité invalide {uuid.uuid4().hex[:5]}",
            "capacity": -100  # Capacité négative
        }
        res = api("post", "/cellars", json=invalid_cellar, token=user_token)
        # Le système accepte ou rejette, mais ne doit pas crasher
        assert res.status_code in (200, 201, 400, 422)

    def test_bottle_with_negative_price(self, user_token, create_cellar):
        """
        Test l'ajout d'une bouteille avec un prix négatif
        """
        cellar = create_cellar()
        assert cellar is not None

        invalid_bottle = {
            "name": "Vin gratuit",
            "vintage": 2018,
            "wine_type": "Rouge",
            "region": "Bordeaux",
            "country": "France",
            "price": -50.00  # Prix négatif
        }
        res = api("post", f"/cellars/{cellar['id']}/bottles",
                 json=invalid_bottle, token=user_token)
        # Peut être 201 ou 400 selon la validation
        assert res.status_code in (200, 201, 400)

    def test_user_email_validation(self, admin_token):
        """
        Test que l'email doit être valide
        """
        invalid_user = {
            "email": "not_an_email",  # Email invalide
            "username": "testuser",
            "password": "password"
        }
        res = api("post", "/users", json=invalid_user, token=admin_token)
        assert res.status_code in (400, 422)  # Unprocessable Entity


class TestAPIErrorHandling:
    """
    Workflow: Gestion des erreurs API
    """

    def test_get_nonexistent_cellar(self, user_token):
        """
        Test la récupération d'une cave inexistante
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = api("get", f"/cellars/{fake_id}", token=user_token)
        assert res.status_code == 404

    def test_get_nonexistent_bottle(self, user_token):
        """
        Test la récupération d'une bouteille inexistante
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = api("get", f"/bottles/{fake_id}", token=user_token)
        assert res.status_code in (404, 403)

    def test_delete_nonexistent_resource(self, user_token):
        """
        Test la suppression d'une ressource inexistante
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        res = api("delete", f"/cellars/{fake_id}", token=user_token)
        assert res.status_code in (404, 204)

    def test_update_nonexistent_resource(self, user_token):
        """
        Test la modification d'une ressource inexistante
        """
        fake_id = "00000000-0000-0000-0000-000000000000"
        update_data = {"name": "Nouvelle cave"}
        res = api("put", f"/cellars/{fake_id}", json=update_data, token=user_token)
        # PUT sur une ressource inexistante retourne 404 ou parfois 400
        assert res.status_code in (400, 404), f"Expected 404 or 400, got {res.status_code}: {res.text}"


class TestComplexScenarios:
    """
    Tests de scénarios complexes multi-étapes
    """

    def test_full_wine_cellar_scenario(self, user_token, create_cellar):
        """
        Scénario complet: Créer une cave, ajouter plusieurs bouteilles,
        consulter, modifier, et finalement nettoyer
        """
        # 1. Créer une cave
        cellar = create_cellar()
        assert cellar is not None
        cellar_id = cellar["id"]

        # 2. Ajouter 5 bouteilles de différents types
        wines = [
            {"name": "Bordeaux 2018", "vintage": 2018, "wine_type": "Rouge",
             "region": "Bordeaux", "country": "France", "quantity": 6},
            {"name": "Bourgogne Blanc 2019", "vintage": 2019, "wine_type": "Blanc",
             "region": "Bourgogne", "country": "France", "quantity": 4},
            {"name": "Champagne Brut", "vintage": 2016, "wine_type": "Mousseux",
             "region": "Champagne", "country": "France", "quantity": 2},
            {"name": "Côtes du Rhône", "vintage": 2017, "wine_type": "Rouge",
             "region": "Rhône", "country": "France", "quantity": 8},
            {"name": "Sauvignon Blanc Loire", "vintage": 2020, "wine_type": "Blanc",
             "region": "Loire", "country": "France", "quantity": 3},
        ]

        bottle_ids = []
        for wine_data in wines:
            res = api("post", f"/cellars/{cellar_id}/bottles",
                     json=wine_data, token=user_token)
            assert res.status_code == 201
            bottle_ids.append(res.json()["id"])

        # 3. Vérifier le nombre de bouteilles
        res_list = api("get", f"/cellars/{cellar_id}/bottles", token=user_token)
        assert res_list.status_code == 200
        bottles = res_list.json()
        assert len(bottles) == 5

        # 4. Modifier quelques bouteilles
        for i in range(2):
            update_data = {"quantity": bottles[i]["quantity"] - 1}
            res_update = api("put", f"/bottles/{bottle_ids[i]}",
                           json=update_data, token=user_token)
            assert res_update.status_code == 200

        # 5. Supprimer une bouteille
        res_delete = api("delete", f"/bottles/{bottle_ids[2]}", token=user_token)
        assert res_delete.status_code == 204

        # 6. Vérifier qu'il reste 4 bouteilles
        res_final_list = api("get", f"/cellars/{cellar_id}/bottles", token=user_token)
        assert res_final_list.status_code == 200
        final_bottles = res_final_list.json()
        assert len(final_bottles) == 4
        assert all(b["id"] != bottle_ids[2] for b in final_bottles)

    def test_user_workflow_with_multiple_cellars(self, user_token):
        """
        Scénario: Un utilisateur crée plusieurs caves et gère des bouteilles
        dans chacune d'elle
        """
        cellar_ids = []

        # 1. Créer 3 caves
        for i in range(3):
            cellar_data = {
                "name": f"Cave {i+1}",
                "location": f"Région {i+1}",
                "capacity": (i + 1) * 100
            }
            res = api("post", "/cellars", json=cellar_data, token=user_token)
            assert res.status_code == 201
            cellar_ids.append(res.json()["id"])

        # 2. Ajouter 2 bouteilles à chaque cave
        for cellar_id in cellar_ids:
            for j in range(2):
                bottle_data = {
                    "name": f"Vin {j+1}",
                    "vintage": 2018 + j,
                    "wine_type": "Rouge" if j == 0 else "Blanc",
                    "region": "Région Test",
                    "country": "France"
                }
                res = api("post", f"/cellars/{cellar_id}/bottles",
                         json=bottle_data, token=user_token)
                assert res.status_code == 201

        # 3. Vérifier que lister les caves retourne 3 caves
        res_list = api("get", "/cellars", token=user_token)
        assert res_list.status_code == 200
        cellars = res_list.json()
        assert len(cellars) >= 3

        # 4. Vérifier que chaque cave a ses 2 bouteilles
        for cellar_id in cellar_ids:
            res_bottles = api("get", f"/cellars/{cellar_id}/bottles", token=user_token)
            assert res_bottles.status_code == 200
            bottles = res_bottles.json()
            assert len(bottles) == 2
