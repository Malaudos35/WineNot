import boto3
from botocore.client import Config
import os
import json

# Configuration MinIO
MINIO_API_URL = os.getenv("MINIO_API_URL", "http://localhost:9000")
MINIO_ROOT_USER = os.getenv("MINIO_ROOT_USER", "minioadmin")
MINIO_ROOT_PASSWORD = os.getenv("MINIO_ROOT_PASSWORD", "minioadmin")
bucket_name = "images"

# Créer une connexion S3 vers MinIO
S3 = boto3.client(
    "s3",
    endpoint_url=MINIO_API_URL,
    aws_access_key_id=MINIO_ROOT_USER,
    aws_secret_access_key=MINIO_ROOT_PASSWORD,
    config=Config(signature_version="s3v4"),
)

def upload_picture(file_path, file_name):
    global S3, bucket_name

    # Créer le bucket (si nécessaire)
    try:
        S3.create_bucket(Bucket=bucket_name)
        print(f"Bucket {bucket_name} créé.")
    except S3.exceptions.BucketAlreadyOwnedByYou:
        pass  # Le bucket existe déjà
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de la création du bucket : {e}"
        }

    # Vérifier si un fichier avec le même nom existe déjà dans le bucket
    try:
        S3.head_object(Bucket=bucket_name, Key=file_name)
        # Supprimer le fichier existant
        S3.delete_object(Bucket=bucket_name, Key=file_name)
        print(f"Fichier existant {file_name} supprimé avant upload.")
    except S3.exceptions.ClientError as e:
        if e.response["Error"]["Code"] != "404":
            return {
                "status": "error",
                "message": f"Erreur lors de la vérification du fichier : {e}"
            }

    # Envoyer le fichier avec le nouveau nom
    try:
        S3.upload_file(file_path, bucket_name, file_name)
        return {
            "status": "success",
            "message": f"Fichier {file_path} envoyé vers MinIO sous le nom {file_name} avec succès !"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors de l'envoi du fichier : {e}"
        }

def download_picture(file_name, local_path):
    global S3, bucket_name

    # Vérifier si le fichier existe dans le bucket
    try:
        S3.head_object(Bucket=bucket_name, Key=file_name)
    except Exception as e:
        return {
            "status": "error",
            "message": f"Le fichier {file_name} n'existe pas dans le bucket {bucket_name}.",
            "error": str(e)
        }

    # Télécharger le fichier
    try:
        S3.download_file(bucket_name, file_name, local_path)
        return {
            "status": "success",
            "message": f"Fichier {file_name} téléchargé avec succès depuis MinIO vers {local_path} !"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Erreur lors du téléchargement du fichier : {e}"
        }

# Test des fonctions
if __name__ == "__main__":
    # Exemple : upload d'un fichier local "mon_image.jpg" vers MinIO avec le nom "ma_nouvelle_image.jpg"
    print("Testing MinIO upload...")
    upload_result = upload_picture("./picture.jpg", "picture.jpg")
    print(json.dumps(upload_result, indent=2))

    print("\nTesting MinIO download...")
    download_result = download_picture("picture.jpg", "./ma_nouvelle_image_telechargee.jpg")
    print(json.dumps(download_result, indent=2))
