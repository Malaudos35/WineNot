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
            "nodes": ACTIVE_NEIGHBORS,
            "seed": SEED
        }), 200

@app.route('/status', methods=['POST'])
def post_status():
    try:
        node = request.form.get('id')
        if node and node not in ACTIVE_NEIGHBORS:
            seed = test_node(node)
            if seed:
                with neighbors_lock:
                    ACTIVE_NEIGHBORS[node] = {"seed": seed}
                return jsonify({"status": f"node {NODE_ID} received"}), 200
        return jsonify({"status": f"node {NODE_ID} in error"}), 300
    except Exception as e:
        logger.error(f"Erreur POST /status")
        return jsonify({"status": "error"}), 500

@app.route('/files', methods=['GET', 'POST'])
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



