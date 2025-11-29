import os
import time
import threading
from threading import Thread
import requests
from flask import Flask, request, send_from_directory, jsonify
import random
import logging

from constantes import *
from fonctions import *
from api import *

def init_node(seed, active_neighbors):
    logger.debug("Démarrage de init_node...")
    with neighbors_lock:
        reload_nodes(active_neighbors)
    global current_leader
    current_leader = get_master(active_neighbors)
    if current_leader:
        syncrinize_file_to_master(current_leader)
    else:
        logger.debug("Aucun leader trouvé.")

def run_flask_app():
    app.run(host='0.0.0.0', port=5000, debug=False)

if __name__ == '__main__':
    # time.sleep(random.randint(1, 10))
    os.makedirs(FILE_DIRECTORY, exist_ok=True)
    logger.debug(f"[{NODE_ID}] Mon SEED est {SEED}")
    logger.debug(f"[{NODE_ID}] Noeuds voisins initiaux : {ALL_NEIGHBORS}")
    
        # Lancement du serveur Flask dans un thread séparé
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    
    with neighbors_lock:
        for nb in ALL_NEIGHBORS:
            ACTIVE_NEIGHBORS[nb] = {"seed": ""}
    # threading.Thread(
    #     target=delayed_init_node,
    #     daemon=True,
    #     args=(SEED, ACTIVE_NEIGHBORS)
    # ).start()
    # app.run(host='0.0.0.0', port=5000, debug=False)

    while True:
        time.sleep(10)
        init_node(SEED, ACTIVE_NEIGHBORS)

logger.warning(f"END {NODE_ID}")