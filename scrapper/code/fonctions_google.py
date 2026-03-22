import os
import requests
from PIL import Image
import cv2
import numpy as np
import io

# from dependencies import GOOGLE_API_KEY, GOOGLE_CSE_ID

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_CSE_ID = os.getenv("GOOGLE_CSE_ID")
def google_search(
    recherche: str,
    search_type: str = "searchTypeUndefined", # or image
    num_results: int = 10,
    api_key: str = GOOGLE_API_KEY,
    cse_id: str = GOOGLE_CSE_ID,
):
    """
    Effectue une recherche Google personnalisée.

    Args:
        recherche (str): Terme de recherche.
        search_type (str): Type de recherche ("image", "web", etc.).
        num_results (int): Nombre de résultats souhaités.
        api_key (str): Clé API Google.
        cse_id (str): ID du moteur de recherche personnalisé (CSE).

    Returns:
        list: Liste des liens des résultats.
    """
    try:
        if not recherche.strip():
            return []

        url = (
            f"https://www.googleapis.com/customsearch/v1?"
            f"key={api_key}&"
            f"cx={cse_id}&"
            f"q={recherche}&"
            f"searchType={search_type}&"
            f"num={num_results}"
        )

        response = requests.get(url)
        data = response.json()

        if response.status_code != 200:
            print(f"Erreur avec l'API Google (code {response.status_code})")
            return []

        lst_results = []
        for item in data.get("items", []):
            lst_results.append(item["link"])

        return lst_results

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
    urls = google_search(name, search_type="image")
    if urls:
        best_image, best_url = select_best_image(urls)
        if best_image:
            # Générer le nom du fichier
            extension = get_file_extension(best_url)
            filename = f"{clean_name(name)}{extension}"
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