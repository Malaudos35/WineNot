# =============================================
# 1. Vérifier que le serveur est accessible
# =============================================
GET http://localhost:5000/clean

HTTP/1.1 200

# =============================================
# 2. Inscription d'un nouvel utilisateur
# =============================================
POST http://localhost:5000/users
Content-Type: application/json
{
  "email": "user@example.com",
  "username": "john_doe",
  "password": "secure_password123"
}

HTTP/1.1 201
Content-Type: application/json
{
  "id": "{{user_id}}",
  "email": "user@example.com",
  "username": "john_doe"
}

# =============================================
# 3. Récupérer les détails de l'utilisateur par email
# =============================================
GET http://localhost:5000/users?email=user@example.com

HTTP/1.1 200
Content-Type: application/json
[{
  "id": "{{user_id}}",
  "email": "user@example.com",
  "username": "john_doe"
}]

# =============================================
# 4. Connexion pour obtenir un token JWT
# =============================================
POST http://localhost:5000/tokens
Content-Type: application/json
{
  "email": "user@example.com",
  "password": "secure_password123"
}

HTTP/1.1 200
Content-Type: application/json
{
  "accessToken": "{{access_token}}",
  "refreshToken": "{{refresh_token}}"
}

# =============================================
# 5. Supprimer l'utilisateur (nécessite un token)
# =============================================
DELETE http://localhost:5000/users/{{user_id}}
Authorization: Bearer {{access_token}}

HTTP/1.1 204

# =============================================
# Variables capturées pour les tests
# =============================================
[Variables]
user_id: string
access_token: string
refresh_token: string
