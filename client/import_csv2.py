#!/usr/bin/env python3
import csv
import requests
import sys
from pathlib import Path

BASE_URL = "http://localhost:5000/api"
CSV_PATH = Path("wine_bottles.csv")

ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin"

USER_EMAIL = "user@example.com"
USER_PASSWORD = "user"


def clean():
    res = requests.get(f"{BASE_URL}/clean")
    if res.status_code != 201:
        print(f"❌ Failed to clean {res.status_code}")
        sys.exit(1)
    print(f"✅ App clean")

def init():
    res = requests.get(f"{BASE_URL}/init")
    if res.status_code != 201:
        print(f"❌ Failed to init {res.status_code}")
        sys.exit(1)
    print(f"✅ App init")

def get_token(email: str, password: str) -> str:
    """Obtain a JWT token for the given credentials."""
    print(f"🔑 Getting token for {email}...")
    res = requests.post(
        f"{BASE_URL}/tokens",
        json={"email": email, "password": password}
    )
    if res.status_code != 201:
        print(f"❌ Failed to get token for {email}: {res.text} {res.status_code}")
        sys.exit(1)
    token = res.json()["token"]
    print(f"✅ Token retrieved for {email}")
    return token


def create_user(admin_token: str, email: str, password: str) -> None:
    """Create a regular user if not already existing."""
    print(f"👤 Creating user {email}...")
    headers = {"Authorization": f"Bearer {admin_token}"}
    res = requests.post(
        f"{BASE_URL}/users",
        json={"email": email, "password": password, "username": email.split("@")[0]},
        headers=headers,
    )
    if res.status_code == 201:
        print(f"✅ User {email} created.")
    elif res.status_code == 400:
        print(f"⚠️  User {email} already exists.")
    else:
        print(f"❌ Error creating user: {res.text}")
        sys.exit(1)


def create_cellar(token: str, name: str, location: str, capacity: int = 100):
    """Create a new cellar for the user."""
    print(f"🏠 Creating cellar '{name}'...")
    headers = {"Authorization": f"Bearer {token}"}
    data = {"name": name, "location": location, "capacity": capacity}
    res = requests.post(f"{BASE_URL}/cellars", json=data, headers=headers)
    if res.status_code not in (200, 201):
        print(f"❌ Failed to create cellar {name}: {res.text}")
        sys.exit(1)
    cellar = res.json()
    print(f"✅ Cellar '{name}' created with id {cellar['id']}")
    return cellar["id"]


def import_bottles(token: str, cellar1_id: str, cellar2_id: str, csv_path: Path):
    """Import wine bottles from CSV and distribute across cellars."""
    print(f"🍷 Importing bottles from {csv_path}...")
    headers = {"Authorization": f"Bearer {token}"}

    with open(csv_path, newline="", encoding="utf-8") as csvfile:
        reader = csv.DictReader(csvfile, delimiter=";")
        bottles = list(reader)

    for i, bottle in enumerate(bottles):
        target_cellar = cellar1_id if i < 5 else cellar2_id

        payload = {
            "name": bottle["name"],
            "vintage": int(bottle["vintage"]) if bottle["vintage"] else None,
            "wine_type": bottle["wine_type"],
            "region": bottle["region"],
            "country": bottle["country"],
            "price": float(bottle["price"]) if bottle["price"] else None,
            "quantity": int(bottle["quantity"]) if bottle["quantity"] else 1,
            # "image_url": bottle["image_url"],
            "notes": bottle["notes"],

            # 👇 AJOUT AUTOMATIQUE DU SCRAPING
            "scrape": True,
        }

        res = requests.post(
            f"{BASE_URL}/cellars/{target_cellar}/bottles",
            json=payload,
            headers=headers,
        )

        if res.status_code in (200, 201):
            print(f"✅ Imported bottle {i+1}/{len(bottles)}: {bottle['name']}")
        else:
            print(f"❌ Failed to import {bottle['name']}: {res.text}")


def main():
    print("🚀 Starting WineNot CSV importer")

    clean()
    init()
    
    # Step 1: Get admin token
    admin_token = get_token(ADMIN_EMAIL, ADMIN_PASSWORD)

    # Step 2: Create user
    create_user(admin_token, USER_EMAIL, USER_PASSWORD)

    # Step 3: Get user token
    user_token = get_token(USER_EMAIL, USER_PASSWORD)

    # Step 4: Create two cellars
    cellar1_id = create_cellar(user_token, "Cellar One", "Rennes")
    cellar2_id = create_cellar(user_token, "Cellar Two", "Saint-Malo")

    # Step 5: Import bottles
    import_bottles(user_token, cellar1_id, cellar2_id, CSV_PATH)

    print("🎉 Import completed successfully!")


if __name__ == "__main__":
    main()
