import requests

node = "http://localhost:5001/files"
url = "https://www.vinsetmillesimes.com/84432-large_default/xpetrus-1987.jpg"
name = "Petrus_1987.jpg"

# Utilisez `data` pour envoyer les données sous forme de formulaire
data = {"url": url, "name": name}
rqt = requests.post(url=node, data=data, timeout=10).json()

print(rqt)

# def send_file(url, node):
#     data = {"url": url}
#     rqt = requests.post(url=node, data=data, timeout=2)
#     if rqt.status_code == 200:
#         return True
    
#     return False
    
    
    
# print(send_file(url, node))