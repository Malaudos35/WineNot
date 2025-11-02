# 🍷 WineNot - Wine Cellar Management API

**WineNot** is a modern web API designed to manage wine cellars, bottles, users, and permissions.  
It’s built with **FastAPI**, **MySQL**, and **Docker**, featuring a clean REST architecture and fully automated tests.

---

## 🚀 Key Features

- 👥 **User Management**
  - Create, update, and delete users.
  - JWT-based authentication and access tokens.
  - Built-in **admin role** with full privileges.

- 🍇 **Wine Cellars & Bottles**
  - Manage multiple cellars per user.
  - Add, update, and delete bottles.
  - Filter and list bottles by cellar and user.

- 🔐 **Permissions & Security**
  - Role-based access control (RBAC) for users and admins.
  - Fine-grained permission management.

- ⚙️ **Database:** MySQL (Dockerized)
- 🧪 **Automated Testing:** Full coverage with `pytest`

---

## 🏗️ Project Structure

```txt
📦 project-root
├── backend/
│   ├── code/
│   │   ├── main.py              → FastAPI entrypoint
│   │   ├── routes/              → API routers (users, cellars, bottles, etc.)
│   │   ├── models.py            → SQLAlchemy ORM models
│   │   ├── schemas.py           → Pydantic schemas
│   │   ├── database.py          → DB connection and initialization
│   │   ├── dependencies.py      → Auth and shared dependencies
│   └── backend.Dockerfile       → Dockerfile for backend service
│
├── db/
│   ├── db.Dockerfile            → Dockerfile for MySQL service
│   ├── sql/
│   │   ├── init-permissions.sh  → Dynamic permissions setup script
│   │   ├── init-permissions.sql → Optional static SQL script
│
├── test/
│   ├── test_api.py              → Complete API tests
│
├── docker-compose.yml
├── requirements.txt
└── README.md

```

---

## 🐳 Getting Started with Docker

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/<your_repo>/WineNot.git
cd WineNot
````

### 2️⃣ Build and Start Containers

```bash
docker compose up --build
```

This starts:

- **MySQL Database** (`db`)
- **FastAPI Backend** (`backend`)

Once running, the backend is available at:
👉 [http://localhost:5000](http://localhost:5000)

---

## ⚙️ Environment Variables

Defined in `docker-compose.yml`:

```yaml
environment:
  - MYSQL_USER=wine_user
  - MYSQL_PASSWORD=secure_password
  - MYSQL_DATABASE=wine_cellar
  - MYSQL_ROOT_PASSWORD=root_password
  - DATABASE_URL=mysql+pymysql://wine_user:secure_password@db:3306/wine_cellar
```

---

## 🔐 MySQL Permissions Initialization

A startup script automatically grants privileges using Docker environment variables.
This ensures permissions stay in sync even if credentials change.

**File:** `db/sql/init-permissions.sh`

```bash
#!/bin/bash
mysql -uroot -p"$MYSQL_ROOT_PASSWORD" <<-EOSQL
  GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}' WITH GRANT OPTION;
  FLUSH PRIVILEGES;
EOSQL
```

---

## 🧪 Running Tests

```bash
cd backend/test
pytest -v
```

Tests include:

- Full API flow (clean + init)
- JWT authentication and token validation
- CRUD operations for:

  - Users
  - Permissions
  - Wine cellars
  - Bottles

Each test automatically connects to the running API via HTTP requests.

---

## 🧰 Useful Commands

### Rebuild and restart everything

```bash
docker compose down -v
docker compose up --build
```

### Access the MySQL CLI

```bash
docker exec -it db mysql -u root -p
```

### Check container logs

```bash
docker logs backend -f
```

---

## 🧑‍💻 Default Authentication

| Role  | Email               | Password |
| ----- | ------------------- | -------- |
| Admin | `admin@example.com` | `admin`  |
| User  | `user@example.com`  | `user`   |

---

## 📜 Example API Usage (via `curl`)

### Get a Token

```bash
curl -X POST "http://localhost:5000/tokens" \
     -H "Content-Type: application/json" \
     -d '{"email": "admin@example.com", "password": "admin"}'
```

### Create a Cellar

```bash
curl -X POST "http://localhost:5000/cellars" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{"name": "Private Cellar", "location": "Basement", "capacity": 50}'
```

### Add a Bottle

```bash
curl -X POST "http://localhost:5000/cellars/<CELLAR_ID>/bottles" \
     -H "Authorization: Bearer <TOKEN>" \
     -H "Content-Type: application/json" \
     -d '{
            "name": "Château Margaux 2015",
            "vintage": 2015,
            "wine_type": "Red",
            "region": "Bordeaux",
            "country": "France",
            "price": 1200.50,
            "quantity": 1,
            "notes": "Grand cru classé"
         }'
```

---

## 🧩 Tech Stack

| Component                  | Technology            |
| -------------------------- | --------------------- |
| **Backend Framework**      | FastAPI               |
| **Database**               | MySQL (Dockerized)    |
| **ORM**                    | SQLAlchemy + SQLModel |
| **Authentication**         | JWT (PyJWT)           |
| **Password Hashing**       | Passlib + bcrypt      |
| **Environment Management** | Python Dotenv         |
| **Testing**                | Pytest                |
| **Deployment**             | Docker Compose        |

---

## 🧱 Requirements (Python Dependencies)

Main dependencies are listed in `requirements.txt`:

```txt
fastapi==0.120.4
uvicorn[standard]==0.38.0
sqlalchemy==2.0.44
sqlmodel==0.0.27
pymysql==1.1.2
psycopg2-binary==2.9.11
pydantic==2.12.3
email-validator==2.3.0
passlib[bcrypt]==1.7.4
bcrypt==4.2.1
pyjwt==2.10.1
python-dotenv==1.2.1
```

---

## 🧠 Troubleshooting

### 🔄 Backend keeps restarting

If Uvicorn reloads continuously, disable auto-reload in `backend.Dockerfile`:

```bash
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "5000"]
```

(remove the `--reload` flag)

### 🔐 Database Connection Fails

The backend automatically retries up to **10 times over 60 seconds** before failing.

---

## 🪪 License

This project is released under the **MIT License**.
You’re free to use, modify, and distribute it as you wish.

---

## ❤️ Acknowledgements

Built with ❤️ using:

- **FastAPI** for modern Python APIs
- **SQLAlchemy** for ORM management
- **Docker** for portability and reproducibility
- **Pytest** for clean and reliable testing

---
