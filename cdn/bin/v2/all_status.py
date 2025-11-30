import requests
nodes = ["localhost:5001", "localhost:5002", "localhost:5003"]
for n in nodes:
    rqt = requests.get(f"http://{n}/status").json()
    print(rqt)


