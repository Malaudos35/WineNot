# 🍷 WineNot - Gestion de Cave à Vin

**WineNot** est une application web moderne permettant de gérer facilement ses caves à vin, bouteilles, utilisateurs et permissions.  
Ce projet repose sur une architecture **FastAPI + MySQL + Docker** et inclut une API REST complète, testée automatiquement avec `pytest`.

## 🚀 Fonctionnalités principales

- 👥 **Gestion des utilisateurs**
  - Création, mise à jour et suppression d’utilisateurs.
  - Authentification via **JWT (JSON Web Token)**.
  - Support d’un **utilisateur admin** avec privilèges étendus.

- 🍇 **Gestion des caves et bouteilles**
  - Créer plusieurs caves à vin.
  - Ajouter, modifier ou supprimer des bouteilles.
  - Filtrer et lister les caves et bouteilles associées à chaque utilisateur.

- 🔐 **Permissions et sécurité**
  - Gestion fine des droits via un système de permissions.
  - Accès restreint selon le rôle (admin / utilisateur standard).

- ⚙️ **Base de données MySQL** intégrée via Docker.
- 🧪 **Tests automatisés** avec `pytest` et appels HTTP directs à l’API.

---

## 🏗️ Architecture technique

```txt
📦 project-root
├── backend/
│   ├── code/
│   │   ├── main.py              → Entrée principale FastAPI
│   │   ├── routes/              → Routes (users, cellars, bottles, etc.)
│   │   ├── models.py            → ORM SQLAlchemy
│   │   ├── schemas.py           → Modèles Pydantic
│   │   ├── database.py          → Connexion et initialisation DB
│   │   ├── dependencies.py      → Authentification et helpers
│   └── backend.Dockerfile       → Image Docker pour l’API
│
├── db/
│   ├── db.Dockerfile            → Image Docker MySQL
│   ├── sql/
│   │   ├── init-permissions.sh  → Script pour accorder les privilèges dynamiques
│   │   ├── init-permissions.sql → (optionnel) Script SQL statique
│
├── test/
│   ├── test_api.py              → Tests complets API
│
├── docker-compose.yml
├── requirements.txt
└── README.md

```

---

## 🐳 Démarrage avec Docker

### 1️⃣ Cloner le dépôt

```bash
git clone git@github.com:Malaudos35/WineNot.git
cd WineNot
````

### 2️⃣ Lancer les conteneurs

```bash
docker compose up --build
```

Cela lancera :

- **MySQL** (`db`)
- **Backend FastAPI** (`backend`)

Le backend sera accessible sur :
👉 [http://localhost:5000](http://localhost:5000)

---

## ⚙️ Variables d’environnement

Définies dans le fichier `docker-compose.yml` :

```yaml
environment:
  - MYSQL_USER=wine_user
  - MYSQL_PASSWORD=secure_password
  - MYSQL_DATABASE=wine_cellar
  - MYSQL_ROOT_PASSWORD=root_password
  - DATABASE_URL=mysql+pymysql://wine_user:secure_password@db:3306/wine_cellar
```

---

## 🔐 Création automatique des permissions MySQL

Le script `db/sql/init-permissions.sh` s’exécute au démarrage du conteneur MySQL et applique les permissions
en utilisant les **variables d’environnement Docker** :

```bash
GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}' WITH GRANT OPTION;
FLUSH PRIVILEGES;
```

---

## 🧪 Lancer les tests

```bash
cd backend/test
pytest -v
```

Les tests effectuent :

- La réinitialisation de la base (`GET /clean` + `GET /init`)
- L’authentification admin (`POST /tokens`)
- Les opérations CRUD complètes sur :

  - Utilisateurs
  - Permissions
  - Caves
  - Bouteilles

---

## 🧰 Commandes utiles

### Recréer entièrement les conteneurs

```bash
docker compose down -v
docker compose up --build
```

### Accéder à la base MySQL

```bash
docker exec -it db mysql -u root -p
```

---

## 🧑‍💻 Authentification par défaut

| Rôle        | Email               | Mot de passe |
| ----------- | ------------------- | ------------ |
| Admin       | `admin@example.com` | `admin`      |
| Utilisateur | `user@example.com`  | `user`       |

---

## 📜 Licence

Projet open-source distribué sous licence MIT.
Tu peux l’adapter librement à tes besoins.

---

## ❤️ Remerciements

Ce projet a été conçu pour illustrer :

- une **architecture backend moderne avec FastAPI**,
- des **tests automatisés complets**,
- une **intégration continue simple via Docker Compose**.

---
