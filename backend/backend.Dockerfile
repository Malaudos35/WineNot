# Utiliser une image Python plus légère pour réduire la surface d'attaque
FROM python:3.11-slim-bookworm

# Définir le répertoire de travail
WORKDIR /app

# Installer les dépendances Python
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
	&& pip install --no-cache-dir --upgrade "setuptools>=80.9.0" "wheel>=0.46.2" \
	&& pip install --no-cache-dir -r requirements.txt

# Exposer le port sur lequel l'application écoute
EXPOSE 5000

# Définir la commande par défaut pour exécuter l'application
CMD ["uvicorn", "main:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]