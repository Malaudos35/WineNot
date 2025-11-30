# Utiliser une image Python officielle comme image de base
FROM python:3.11

# Définir le répertoire de travail dans le conteneur
WORKDIR /tmp

ENV DEBIAN_FRONTEND=noninteractive

# Installer tzdata pour les informations de fuseau horaire
RUN apt-get update 
RUN apt-get upgrade -y
RUN apt-get install -y tzdata \
    libnspr4\
    libnss3\
    libdbus-1-3\
    libatk1.0-0t64\
    libatk-bridge2.0-0t64\
    libcups2t64\
    libxkbcommon0\
    libatspi2.0-0t64\
    libxcomposite1\
    libxdamage1\
    libxfixes3\
    libxrandr2\
    libgbm1\
    libasound2t64 >> /dev/null
    # libXcursor.so.1\
    # libgtk-3.so.0\
    # libgdk-3.so.0
RUN pip install --upgrade pip

# Copier le fichier requirements.txt dans le conteneur
COPY requirements.txt .

# Installer les dépendances Python
RUN pip install --no-cache-dir --quiet --no-warn-script-location -r requirements.txt

# Installer les navigateurs nécessaires pour Playwright
RUN playwright install >> /dev/null
RUN playwright install-deps >> /dev/null

WORKDIR /app

# Exposer le port sur lequel l'application écoute
EXPOSE 5000

# Définir la commande par défaut pour exécuter l'application
CMD ["uvicorn", "main:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]
