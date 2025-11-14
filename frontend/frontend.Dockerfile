# Utilise une image officielle PHP avec Apache
FROM php:8.2-apache

# Installe uniquement les dépendances nécessaires pour pdo_mysql
RUN apt-get update && apt-get install -y --no-install-recommends \
    default-libmysqlclient-dev \
    && rm -r /var/lib/apt/lists/* \
    && docker-php-ext-install pdo pdo_mysql

# Active les modules Apache
RUN a2enmod rewrite

# Donne les permissions nécessaires
RUN chown -R www-data:www-data /var/www/html/

# Expose le port 80
EXPOSE 80

# Démarre Apache
CMD ["apache2-foreground"]
