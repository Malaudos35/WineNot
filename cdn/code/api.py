"""
Module contenant les routes API pour l'application.

Ce module définit les endpoints pour synchroniser les fichiers, obtenir le statut des nœuds,
lister et télécharger des fichiers, et gérer les interactions entre les nœuds.
"""

import os
from flask import request, send_from_directory, jsonify
import requests
from constantes import (
    app, ALL_NEIGHBORS, neighbors_lock, FILE_DIRECTORY,
    NODE_ID, MASTER, SLAVES, SEED, logger
)
from fonctions import syncrinize_file_to_master, download_file_from_url, brodcast_file

@app.route('/sync', methods=['GET'])
def sync():
    """
    Synchronise les fichiers avec tous les voisins.

    Returns:
        Response: Un objet JSON indiquant que le nœud est actif.
    """
    for n in ALL_NEIGHBORS:
        syncrinize_file_to_master(n)
    with neighbors_lock:
        return jsonify({"status": "alive"}), 200

@app.route('/status', methods=['GET'])
def get_status():
    """
    Retourne le statut du nœud, incluant le nombre de fichiers, le maître, les esclaves et la seed.

    Returns:
        Response: Un objet JSON contenant les informations de statut du nœud.
    """
    total_files = sum(len(files) for _, _, files in os.walk(FILE_DIRECTORY))
    with neighbors_lock:
        return jsonify({
            "status": "alive",
            "node": NODE_ID,
            "files": total_files,
            "master": MASTER,
            "slaves": SLAVES,
            "seed": SEED
        }), 200

@app.route('/files', methods=['GET', 'POST'])
def list_files():
    """
    Gère les requêtes pour lister les fichiers ou télécharger un fichier depuis une URL.

    Returns:
        Response: Un objet JSON contenant la liste des fichiers ou le statut de téléchargement.
    """
    if request.method == 'POST':
        try:
            url = request.form.get('url')
            name = request.form.get('name')
            if name is None:
                name = ""
            if not url:  # Vérification des paramètres obligatoires
                return jsonify({"status": "missing url parameter"}), 400
            # Téléchargement du fichier
            result = download_file_from_url(url, FILE_DIRECTORY, filname=name)
            if result:
                logger.debug(f"[{NODE_ID}] Fichier {url} reçu et sauvegardé sous {os.path.basename(result)}.")
                brodcast_file(ALL_NEIGHBORS, name)
                return jsonify({"status": "file received", "filename": os.path.basename(result)}), 200
            return jsonify({"status": "failed to download file"}), 500
        except (requests.exceptions.RequestException, ValueError, KeyError, IOError) as e:
            logger.error(f"[{NODE_ID}] Erreur POST /files: {str(e)}")
            return jsonify({"status": "error", "message": str(e)}), 500
    else:  # GET
        files = os.listdir(FILE_DIRECTORY)
        return jsonify({"files": files})

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    """
    Retourne un fichier spécifique.

    Args:
        filename (str): Le nom du fichier à retourner.

    Returns:
        Response: Le fichier demandé ou un message d'erreur.
    """
    try:
        return send_from_directory(FILE_DIRECTORY, filename)
    except (FileNotFoundError, IOError) as e:
        logger.error(f"[{NODE_ID}] Erreur GET /files/{filename}")
        return jsonify({"status": "error", "message": str(e)}), 500
