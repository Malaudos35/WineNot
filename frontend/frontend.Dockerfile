# Utilise une image officielle PHP avec Apache
FROM php:8.2-apache-bookworm

# Eviter les prompts interactifs
ENV DEBIAN_FRONTEND=noninteractive

# Mettre à jour les paquets système pour corriger vulnérabilités connues,
# puis nettoyer le cache apt pour réduire la taille de l'image.
RUN apt-get update \
	&& apt-get upgrade -y \
	&& apt-get clean \
	&& rm -rf /var/lib/apt/lists/*

# pdo_mysql utilise mysqlnd; aucune dépendance apt supplémentaire n'est requise
RUN docker-php-ext-install pdo pdo_mysql

# Active les modules Apache
RUN a2enmod rewrite

# Donne les permissions nécessaires
RUN chown -R www-data:www-data /var/www/html/

# Expose le port 80
EXPOSE 80

# Démarre Apache
CMD ["apache2-foreground"]
