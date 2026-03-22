# routes/google.py
from fastapi import APIRouter, Depends, status, Request, Query

from dependencies import API_PATH_ROOT
from fonctions_google import google_search, select_best_image, get_file_extension, clean_name


router = APIRouter(prefix=API_PATH_ROOT, tags=["admin"])

@router.get("/search", status_code=status.HTTP_200_OK)
def google(
    q: str = Query(..., description="Terme de recherche"),
    limit: int = Query(10, description="Nombre maximum de résultats"),
    image: bool = Query(False, description="Rechercher des images ?")
):
    print(q, limit, image)
    # Logique de recherche ici
    return {"q": q, "limit": limit, "image": image}


@router.get("/search/image/<requete>", status_code=status.HTTP_200_OK)
def google_images(requete):
    # print(q, limit, image)
    # Logique de recherche ici
    # return {"q": q, "limit": limit, "image": image}
    recherche = requete
    urls = google_search(recherche, search_type="image")
    if urls:
        best_image, best_url = select_best_image(urls)
        if best_image:
            # Générer le nom du fichier
            extension = get_file_extension(best_url)
            filename = f"{clean_name(recherche)}{extension}"
            # best_image.save(filename)
            print(f"L'image la plus pertinente a été sauvegardée sous '{filename}'.")
            return { "url" : filename }
        else:
            print("Aucune image pertinente trouvée.")
    else:
        print("Aucune URL d'image trouvée.", urls)

    return False

    pass