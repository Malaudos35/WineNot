"""
Module contenant les routes API pour l'application.
Ce module définit les endpoints pour synchroniser les fichiers, obtenir le statut des nœuds,
lister et télécharger des fichiers, et gérer les interactions entre les nœuds.
"""
import os
from typing import Optional
from fastapi import HTTPException, Form
from fastapi.responses import FileResponse, JSONResponse

from constantes import (
    NODE_ID, ALL_NEIGHBORS, neighbors_lock, FILE_DIRECTORY,
    MASTER, SLAVES, SEED, logger
)
from fonctions import syncrinize_file_to_master, download_file_from_url, brodcast_file, app

@app.get("/sync")
async def sync():
    """
    Synchronise les fichiers avec tous les voisins.
    Returns:
        JSONResponse: Un objet JSON indiquant que le nœud est actif.
    """
    for neighbor in ALL_NEIGHBORS:
        syncrinize_file_to_master(neighbor)
    with neighbors_lock:
        return JSONResponse(content={"status": "alive"}, status_code=200)

@app.get("/status")
async def get_status():
    """
    Retourne le statut du nœud, incluant le nombre de fichiers, le maître, les esclaves et la seed.
    Returns:
        JSONResponse: Un objet JSON contenant les informations de statut du nœud.
    """
    total_files = sum(len(files) for _, _, files in os.walk(FILE_DIRECTORY))
    with neighbors_lock:
        return JSONResponse(content={
            "status": "alive",
            "node": NODE_ID,
            "files": total_files,
            "master": MASTER,
            "slaves": SLAVES,
            "seed": SEED
        }, status_code=200)

@app.post("/files")
async def upload_file(url: str = Form(...), name: Optional[str] = Form(None)):
    """
    Télécharge un fichier depuis une URL et le sauvegarde localement.
    Args:
        url (str): L'URL du fichier à télécharger.
        name (str, optional): Le nom sous lequel sauvegarder le fichier.
    Returns:
        JSONResponse: Un objet JSON indiquant le statut du téléchargement.
    """
    try:
        if not url:
            raise HTTPException(status_code=400, detail="Missing URL parameter")

        filename = name if name else os.path.basename(url)
        result = download_file_from_url(url, FILE_DIRECTORY, filname=filename)

        if result:
            logger.debug(f"[{NODE_ID}] Fichier {url} reçu et sauvegardé sous {os.path.basename(result)}.")
            brodcast_file(ALL_NEIGHBORS, filename)
            return JSONResponse(content={"status": "file received",
                                         "filename": os.path.basename(result)}, status_code=200)
        raise HTTPException(status_code=500, detail="Failed to download file")
    except Exception as exc:
        logger.error(f"[{NODE_ID}] Erreur POST /files: {str(exc)}")
        raise HTTPException(status_code=500, detail=str(exc)) from exc

@app.get("/files")
async def list_files():
    """
    Liste les fichiers disponibles dans le répertoire local.
    Returns:
        JSONResponse: Un objet JSON contenant la liste des fichiers.
    """
    files = os.listdir(FILE_DIRECTORY)
    return JSONResponse(content={"files": files}, status_code=200)

@app.get("/files/{filename}")
async def get_file(filename: str):
    """
    Retourne un fichier spécifique.
    Args:
        filename (str): Le nom du fichier à retourner.
    Returns:
        FileResponse: Le fichier demandé.
    Raises:
        HTTPException: Si le fichier n'existe pas.
    """
    filepath = os.path.join(FILE_DIRECTORY, filename)
    if not os.path.exists(filepath):
        logger.error(f"[{NODE_ID}] Fichier {filename} non trouvé.")
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(filepath)
