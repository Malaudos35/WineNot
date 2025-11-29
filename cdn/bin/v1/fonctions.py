import os
import requests
from urllib.parse import urlparse
import time

from constantes import *


def download_file_from_url(url: str, file_directory: str, max_retries=3) -> str:
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


def syncrinize_file_to_master(node: str):
    try:
        local_files = os.listdir(FILE_DIRECTORY)
        
        url = f"http://{node}/files"
        distants_files = requests.get(url, timeout=10).json().get("files", [])
        
        for fls in distants_files:
            if fls in local_files:
                distants_files.remove(fls)
        
        for filename in distants_files: # get files
            file_url = f"http://{node}/files/{filename}"
            download_file_from_url(file_url, FILE_DIRECTORY)
            logger.debug(f"[{node}] Fichier {filename} synchronisé.")
    except Exception as e:
        logger.error(f"[{node}] Erreur synchronisation: {str(e)}")

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
    for nb in list(active_neighbors.keys()):
        seed = test_node(nb)
        if not seed:
            active_neighbors[nb] = {"seed": "0"}    # del
            logger.debug(f"Noeud {nb} inactif.")
        else:
            active_neighbors[nb] = {"seed": str(seed)}
            logger.debug(f"Seed du noeud {nb} mis à jour: {seed}")

def get_master(neighbors: dict):
    master = None
    max_seed = -1
    for nb, data in neighbors.items():
        seed = int(data.get("seed", 0))
        if seed > max_seed:
            max_seed = seed
            master = nb
    return master
