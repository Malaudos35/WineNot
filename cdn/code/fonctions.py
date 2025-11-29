"""
Module contenant les fonctions utilitaires pour l'application.

Ce module fournit des fonctions pour télécharger des fichiers, synchroniser des fichiers
avec un maître, tester la disponibilité des nœuds, recharger les nœuds actifs, envoyer des fichiers,
et diffuser des fichiers vers plusieurs nœuds.
"""

import os
import time
from urllib.parse import urlparse
import multiprocessing
import requests
from constantes import logger, FILE_DIRECTORY, NODE_ID

def download_file_from_url(url: str, file_directory: str, filname="", max_retries=3):
    """
    Télécharge un fichier depuis une URL et le sauvegarde dans un répertoire donné.

    Args:
        url (str): L'URL du fichier à télécharger.
        file_directory (str): Le répertoire où sauvegarder le fichier.
        filname (str, optional): Le nom personnalisé pour le fichier. Par défaut, utilise l'URL.
        max_retries (int, optional): Le nombre de tentatives de téléchargement. Par défaut, 3.

    Returns:
        str: Le chemin du fichier téléchargé si réussi, sinon False.
    """
    for attempt in range(max_retries):
        try:
            parsed_url = urlparse(url)
            if not all([parsed_url.scheme, parsed_url.netloc]):
                raise ValueError(f"URL invalide: {url}")
            # Utiliser le nom de fichier fourni ou extraire le nom de l'URL
            if filname:
                filename = filname
            else:
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
    """
    Synchronise les fichiers locaux avec ceux du maître.

    Args:
        node (str): L'adresse du nœud maître.

    Returns:
        bool: True si la synchronisation a réussi, sinon False.
    """
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
            except requests.exceptions.RequestException as e:
                logger.error(f"Échec de la synchronisation du fichier {filename}: {str(e)}")
                return False
        return True
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        logger.error(f"Erreur de synchronisation avec {node}: {str(e)}")
        return False

def test_node(node: str):
    """
    Teste la disponibilité d'un nœud et récupère sa seed.

    Args:
        node (str): L'adresse du nœud à tester.

    Returns:
        str: La seed du nœud si disponible, sinon False.
    """
    try:
        url = f"http://{node}/status"
        req = requests.get(url, timeout=5).json()
        node_id = req.get("node")
        seed = req.get("seed")
        if node_id and seed:
            return seed
        return False
    except (requests.exceptions.RequestException, ValueError, KeyError) as e:
        logger.error(f"Erreur test noeud {node}: {str(e)}")
        return False

def reload_nodes(active_neighbors: dict):
    """
    Recharge la liste des nœuds actifs et leurs seeds.

    Args:
        active_neighbors (dict): Dictionnaire des nœuds actifs.

    Returns:
        dict: Dictionnaire mis à jour des nœuds actifs et leurs seeds.
    """
    new_active_neighbors = {}
    for nb in active_neighbors:
        seed = test_node(nb)
        if seed:
            new_active_neighbors[nb] = {"seed": str(seed)}
            logger.warning(f"[{NODE_ID}] Noeud {nb} actif avec seed {seed}")
        else:
            logger.error(f"[{NODE_ID}] Noeud {nb} inactif")
    return new_active_neighbors

def send_file(url, node):
    """
    Envoie un fichier à un nœud donné.

    Args:
        url (str): L'URL du fichier à envoyer.
        node (str): L'adresse du nœud destinataire.

    Returns:
        bool: True si l'envoi a réussi, sinon False.
    """
    data = {"url": url}
    try:
        rqt = requests.post(url=node, data=data, timeout=2)
        if rqt.status_code == 200:
            return True
    except requests.exceptions.RequestException as e:
        logger.error(f"Erreur lors de l'envoi du fichier à {node}: {str(e)}")
    return False

def brodcast_file(list_neighbor, filename):
    """
    Diffuse un fichier vers plusieurs nœuds en parallèle.

    Args:
        list_neighbor (list): Liste des adresses des nœuds voisins.
        filename (str): Le nom du fichier à diffuser.

    Returns:
        bool: True si toutes les diffusions ont réussi, sinon False.
    """
    url = f"http://{NODE_ID}/files/{filename}"
    # Utilisation de multiprocessing.Pool pour paralléliser les requêtes
    with multiprocessing.Pool(processes=len(list_neighbor)) as pool:
        # Créer une liste d'arguments pour send_file
        args = [(url, f"http://{n}/files") for n in list_neighbor]
        logger.warning(args)
        # Lancer send_file en parallèle
        results = pool.starmap(send_file, args)
    return all(results)  # Retourne True si toutes les requêtes ont réussi
