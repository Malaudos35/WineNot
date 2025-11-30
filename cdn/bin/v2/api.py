# api.py
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


# @app.route('/init', methods=['GET'])
# def init():
#     total_files = sum(len(files) for _, _, files in os.walk(FILE_DIRECTORY))
#     with neighbors_lock:
#         return jsonify({
#             "status": "alive",
#             "node": NODE_ID,
#             "files": total_files,
#             "nodes": ACTIVE_NEIGHBORS,
#             "seed": SEED
#         }), 200

@app.route('/status', methods=['GET'])
def get_status():
    total_files = sum(len(files) for _, _, files in os.walk(FILE_DIRECTORY))
    with neighbors_lock:
        return jsonify({
            "status": "alive",
            "node": NODE_ID,
            "files": total_files,
            "master": MASTER,  # Utilisez la variable globale MASTER
            "slaves": SLAVES,
            "seed": SEED
        }), 200


@app.route('/add_slave', methods=['POST'])
def add_slave():
    try:
        node_id = request.form.get('id')
        if not node_id:
            return jsonify({"status": "missing node id"}), 400

        # Vérifier que le nœud est actif
        seed = test_node(node_id)
        if not seed:
            return jsonify({"status": f"node {node_id} is not reachable"}), 400

        # Ajouter le nœud esclave
        with neighbors_lock:
            if node_id not in SLAVES:
                SLAVES[node_id] = {"seed": seed}
                logger.warning(f"[{NODE_ID}] Nouvel esclave ajouté : {node_id} (seed: {seed})")
                return jsonify({"status": f"node {node_id} added as slave"}), 200
            else:
                return jsonify({"status": f"node {node_id} already a slave"}), 300
    except Exception as e:
        logger.error(f"[{NODE_ID}] Erreur POST /add_slave: {str(e)}")
        return jsonify({"status": "error"}), 500



@app.route('/files', methods=['GET', 'POST']) # add put delete
def list_files():
    if request.method == 'POST':
        try:
            node = request.form.get('id')
            action = request.form.get('action')
            file = request.files.get('file')
            if node and action and file:
                url = f"http://{node}/files/{file.filename}"
                download_file_from_url(url, FILE_DIRECTORY)
                logger.debug(f"[{NODE_ID}] Fichier {file.filename} reçu et sauvegardé.")
                return jsonify({"status": "file received"}), 200
            return jsonify({"status": "missing parameters"}), 400
        except Exception as e:
            logger.error(f"[{NODE_ID}] Erreur POST /files")
            return jsonify({"status": "error", "message": str(e)}), 500
    else:
        files = os.listdir(FILE_DIRECTORY)
        return jsonify({"files": files})

@app.route('/files/<filename>', methods=['GET'])
def get_file(filename):
    try:
        return send_from_directory(FILE_DIRECTORY, filename)
    except Exception as e:
        logger.error(f"[{NODE_ID}] Erreur GET /files/{filename}")
        return jsonify({"status": "error", "message": str(e)}), 500



