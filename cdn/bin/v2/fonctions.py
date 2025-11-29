# fonctions.py
import os
import requests
from urllib.parse import urlparse
import time

from constantes import *


def download_file_from_url(url: str, file_directory: str, max_retries=3):
    for attempt in range(max_retries):
        try:
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise ValueError(f"URL invalide: {url}")
            filename = os.path.basename(parsed_url.path)
            if not filename:
                raise ValueError("Nom de fichier introuvable dans l'URL.")
            file_path = os.path.join(file_directory, filename)
            logger.debug(f"Téléchargement du fichier depuis {url} (tentative {attempt + 1})...")

            response = requests.get(url, stream=True, timeout=30, allow_redirects=True)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            logger.debug(f"Fichier téléchargé: {file_path}")
            return file_path
        except requests.exceptions.RequestException as e:
            logger.debug(f"Erreur téléchargement {url} (tentative {attempt + 1}): {str(e)}")
            if attempt == max_retries - 1:
                raise
            time.sleep(2)  # Attendre avant de réessayer
    return False

def syncrinize_file_to_master(node: str):
    try:
        local_files = set(os.listdir(FILE_DIRECTORY))
        url = f"http://{node}/files"
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        distant_files = set(response.json().get("files", []))

        # Télécharger les fichiers manquants
        for filename in distant_files - local_files:
            file_url = f"http://{node}/files/{filename}"
            try:
                download_file_from_url(file_url, FILE_DIRECTORY)
                logger.debug(f"Fichier {filename} synchronisé depuis {node}.")
            except Exception as e:
                logger.error(f"Échec de la synchronisation du fichier {filename}: {str(e)}")
                return False
        return True
    except Exception as e:
        logger.error(f"Erreur de synchronisation avec {node}: {str(e)}")
        return False

def test_node(node: str):
    try:
        url = f"http://{node}/status"
        req = requests.get(url, timeout=5).json()  # Timeout augmenté
        node_id = req.get("node")
        seed = req.get("seed")
        if node_id and seed:
            return seed
        return False
    except Exception as e:
        logger.error(f"Erreur test noeud {node}: {str(e)}")
        return False

def reload_nodes(active_neighbors: dict):
    new_active_neighbors = {}
    for nb in ALL_NEIGHBORS:
        seed = test_node(nb)
        if seed:
            new_active_neighbors[nb] = {"seed": str(seed)}
            logger.warning(f"[{NODE_ID}] Noeud {nb} actif avec seed {seed}")
        else:
            logger.error(f"[{NODE_ID}] Noeud {nb} inactif")
    return new_active_neighbors


def get_master(neighbors: dict):
    max_seed = -1
    master = ""
    for node, data in neighbors.items():
        seed = int(data.get("seed", 0))
        logger.warning(f"[{NODE_ID}] Vérification du nœud {node} avec seed {seed}")
        if seed > max_seed:
            max_seed = seed
            master = node
    logger.warning(f"[{NODE_ID}] Maître élu : {master} avec seed {max_seed}")
    return master


def notify_master(master: str):
    if not master or master == NODE_ID:
        return False

    try:
        url = f"http://{master}/add_slave"
        data = {"id": NODE_ID}
        response = requests.post(url, data=data, timeout=5)
        if response.status_code == 200:
            logger.warning(f"[{NODE_ID}] Enregistré comme esclave auprès de {master}.")
            return True
        else:
            logger.error(f"[{NODE_ID}] Échec de l'enregistrement : {response.status_code}")
            return False
    except Exception as e:
        logger.error(f"[{NODE_ID}] Erreur lors de la notification : {str(e)}")
        return False



