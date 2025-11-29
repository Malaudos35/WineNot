# constantes.py
import os
import random
import threading
from threading import Thread
import logging
from flask import Flask, request, send_from_directory, jsonify

# Configuration
NODE_ID = os.getenv("NODE_ID", "node1:5000")
ALL_NEIGHBORS = os.getenv("NEIGHBORS", "node1:5000,node2:5000,node3:5000").split(",")
try:
    ALL_NEIGHBORS.remove(NODE_ID)
except ValueError:
    pass

FILE_DIRECTORY = "/data"
SEED = str(os.getenv("SEED", random.randint(100, 999)))
os.environ["SEED"]=SEED

HEARTBEAT_INTERVAL = 10
HEARTBEAT_TIMEOUT = 5  # Augmenté pour éviter les timeouts

# Variables partagées protégées par verrou
ACTIVE_NEIGHBORS = {}
MASTER = "" # 0,1 master
SLAVES = {} # 0,All slaves

neighbors_lock = threading.Lock()

logger = logging

app = Flask(__name__)

