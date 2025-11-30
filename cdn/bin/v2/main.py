# main.py
import os
import time
# import threading
from threading import Thread
# import requests
from flask import Flask, request, send_from_directory, jsonify
# import random
# import logging

from constantes import *
from fonctions import *
from api import *

def init_node(active_neighbors):
    global ACTIVE_NEIGHBORS, MASTER, SLAVES
    logger.warning(f"[{NODE_ID}] Démarrage de init_node...")

    with neighbors_lock:
        ACTIVE_NEIGHBORS = reload_nodes(active_neighbors)
        ACTIVE_NEIGHBORS[NODE_ID] = {"seed": SEED}
        new_master = get_master(ACTIVE_NEIGHBORS)

        if new_master != NODE_ID and int(SEED) > int(ACTIVE_NEIGHBORS.get(new_master, {}).get("seed", 0)):
            new_master = NODE_ID
            logger.warning(f"[{NODE_ID}] Ma seed ({SEED}) est supérieure, je deviens maître.")

        if new_master != MASTER:
            logger.warning(f"[{NODE_ID}] Mise à jour du maître : {new_master}")
            MASTER = new_master  # Mise à jour de MASTER sous verrou

            if MASTER == NODE_ID:
                logger.warning(f"[{NODE_ID}] Je suis le maître.")
                SLAVES = {}  # Réinitialisation des esclaves
            else:
                logger.warning(f"[{NODE_ID}] Je ne suis pas le maître, je m'enregistre comme esclave.")
                notify_master(MASTER)


def run_flask_app():
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    logger.warning("Main function")
    os.makedirs(FILE_DIRECTORY, exist_ok=True)
    logger.debug(f"[{NODE_ID}] Mon SEED est {SEED}")
    logger.debug(f"[{NODE_ID}] Noeuds voisins initiaux : {ALL_NEIGHBORS}")

    # Lancement du serveur Flask dans un thread séparé
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()

    # Attendre que le serveur Flask soit prêt
    time.sleep(20)

    while True:
        try:
            init_node(ACTIVE_NEIGHBORS)
        except Exception as e:
            logger.error(f"Erreur dans init_node: {str(e)}")
        time.sleep(HEARTBEAT_INTERVAL)




if __name__ == '__main__':
    main()

logger.warning(f"END {NODE_ID}")