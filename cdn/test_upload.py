import requests
import os
import time

node = "localhost:5003"  # Remplacez par l'adresse du nœud que vous souhaitez tester
url = f"http://{node}/files"
response = requests.post(url, json={"id": "node1:5000", "file": "picture.jpg"})

print(f"Statut de la réponse: {response.status_code}")
print(f"Contenu de la réponse: {response.text}")