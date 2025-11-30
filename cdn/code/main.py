"""
Module principal de l'application.

Ce module initialise le nœud, lance le serveur Flask et gère la synchronisation
des fichiers avec les voisins.
"""

import os
import time
from threading import Thread
import requests
from constantes import HEARTBEAT_INTERVAL
from fonctions import syncrinize_file_to_master
from api import logger, NODE_ID, neighbors_lock, ALL_NEIGHBORS, app, FILE_DIRECTORY, SEED

def init_node():
    """
    Initialise le nœud en synchronisant les fichiers avec tous les voisins.
    """
    logger.warning(f"[{NODE_ID}] Démarrage de init_node...")
    with neighbors_lock:
        for n in ALL_NEIGHBORS:
            syncrinize_file_to_master(n)

def run_flask_app():
    """
    Lance le serveur Flask.
    """
    app.run(host='0.0.0.0', port=5000, debug=False)

def main():
    """
    Fonction principale du programme.

    Initialise le nœud, lance le serveur Flask et gère la synchronisation périodique.
    """
    logger.warning("Main function")
    os.makedirs(FILE_DIRECTORY, exist_ok=True)
    logger.debug(f"[{NODE_ID}] Mon SEED est {SEED}")
    logger.debug(f"[{NODE_ID}] Noeuds voisins initiaux : {ALL_NEIGHBORS}")
    # Lancement du serveur Flask dans un thread séparé
    flask_thread = Thread(target=run_flask_app, daemon=True)
    flask_thread.start()
    # Attendre que le serveur Flask soit prêt
    time.sleep(10)
    for _ in range(3):
        try:
            init_node()
        except requests.exceptions.RequestException as e:
            logger.error(f"Erreur dans init_node: {str(e)}")
        time.sleep(HEARTBEAT_INTERVAL)
    while True:
        time.sleep(10)

if __name__ == '__main__':
    main()
