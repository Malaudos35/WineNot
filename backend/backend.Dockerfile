# Utiliser une image Python officielle comme image de base
FROM python:3.11

# Définir le répertoire de travail dans le conteneur
WORKDIR /tmp

# Installer tzdata pour les informations de fuseau horaire
RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install -y tzdata

RUN pip install --upgrade pip

# Définir le fuseau horaire sur Paris
ENV TZ=Europe/Paris

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app

# Exposer le port sur lequel l'application écoute
EXPOSE 5000

# Définir la commande par défaut pour exécuter l'application
CMD ["uvicorn", "main:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]
