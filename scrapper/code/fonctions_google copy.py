import os
import requests
from PIL import Image
import cv2
import numpy as np
import io

from dependencies import GOOGLE_API_KEY, GOOGLE_CSE_ID

def google_search(recherche):
    try:
        if recherche.replace(" ", "") == "":
            return []
        url = f"https://www.googleapis.com/customsearch/v1?key={GOOGLE_API_KEY}&cx={GOOGLE_CSE_ID}&q={recherche}&searchType=image"
        response = requests.get(url)
        data = response.json()
        print(response.status_code)
        if response.status_code != 200:
            print("Erreur token api")
            return []
        lst_images = []
        for item in data.get("items", []):
            lst_images.append(item["link"])
        return lst_images
    except Exception as e:
        print(f"Erreur lors de la recherche Google: {e}")
        return []

def download_image(url):
    """Télécharge une image depuis une URL."""
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return Image.open(io.BytesIO(response.content))
    except Exception as e:
        print(f"Erreur lors du téléchargement de {url}: {e}")
    return None

def detect_bottle(image):
    """Détecte si une bouteille est présente dans l'image (méthode simple)."""
    img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    for contour in contours:
        area = cv2.contourArea(contour)
        if 5000 < area < 50000:
            return True
    return False

def get_file_extension(url):
    """Extrait l'extension du fichier depuis l'URL."""
    filename = os.path.basename(url)
    return os.path.splitext(filename)[1]

def select_best_image(urls):
    """Sélectionne l'image la plus pertinente et retourne son URL."""
    best_image = None
    best_resolution = 0
    best_bottle_score = 0
    best_url = None

    for url in urls:
        image = download_image(url)
        if image is None:
            continue
        resolution = image.size[0] * image.size[1]
        bottle_score = 1 if detect_bottle(image) else 0
        if (bottle_score > best_bottle_score) or (bottle_score == best_bottle_score and resolution > best_resolution):
            best_image = image
            best_resolution = resolution
            best_bottle_score = bottle_score
            best_url = url

    return best_image, best_url

def clean_name(name):
    # Remplace les espaces et les tirets par des underscores, puis sépare les mots
    mots = name.lower().replace(" ", "_").replace("-", "_").replace("+", "_").split("_")
    # Met en majuscule la première lettre de chaque mot
    mots_capitalises = [mot.capitalize() for mot in mots]
    # Rejoint les mots avec un underscore
    return "_".join(mots_capitalises)

# Exécuter le script
def download_wine_image(name):
    urls = google_search(name)
    if urls:
        best_image, best_url = select_best_image(urls)
        if best_image:
            # Générer le nom du fichier
            extension = get_file_extension(best_url)
            filename = f"{clean_name(recherche)}{extension}"
            best_image.save(filename)
            print(f"L'image la plus pertinente a été sauvegardée sous '{filename}'.")
            return { "file" : filename }
        else:
            print("Aucune image pertinente trouvée.")
    else:
        print("Aucune URL d'image trouvée.", urls)

    return False

if __name__ == "__main__":
    recherche = "bouteille petrus 1987"
    print(download_wine_image(recherche))