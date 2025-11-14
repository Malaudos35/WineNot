#!/bin/bash
set -e
echo "Applying dynamic MySQL user permissions..."

# Attends que MySQL soit prêt
until mysql -h localhost -u root -p"$MYSQL_ROOT_PASSWORD" -e "SELECT 1" &> /dev/null; do
  echo "Waiting for MySQL..."
  sleep 2
done

# Crée l'utilisateur s'il n'existe pas
mysql -h localhost -u root -p"$MYSQL_ROOT_PASSWORD" <<-EOSQL
    CREATE USER IF NOT EXISTS '${MYSQL_USER}'@'%' IDENTIFIED BY '${MYSQL_PASSWORD}';
    GRANT ALL PRIVILEGES ON *.* TO '${MYSQL_USER}'@'%' WITH GRANT OPTION;
    FLUSH PRIVILEGES;
EOSQL

echo "Permissions applied for user '${MYSQL_USER}'@'%'"
