import os
import requests
import logging
from urllib.parse import urlparse
import time

logger = logging

FILE_DIRECTORY = "../data"  # Chemin du dossier à analyser

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




syncrinize_file_to_master("localhost:5001")

