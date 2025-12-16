.PHONY: all venv build test_unitaires

# Cible par défaut : affiche les commandes sans les exécuter
default:
	@echo "Commandes disponibles :"
	@echo "  make all       - Exécute toutes les commandes"
	@echo "  make venv      - Crée l'environnement virtuel et installe les dépendances"
	@echo "  make build     - Construit et lance les conteneurs Docker en arriere plan"
	@echo "  make lunch     - Construit et lance les conteneurs Docker en interactif"
	@echo "  make linter    - Lance le linter sur le code python"
	@echo "  make test_unitaires - Exécute les tests unitaires"

# Cible pour tout exécuter
all: venv build test_unitaires

# Crée et active un environnement virtuel, puis installe les dépendances
venv:
	@python -m venv venv
	@. venv/bin/activate && pip install -r backend/requirements.txt
	@. venv/bin/activate && pip install -r scrapper/requirements.txt

# Lance la construction et le démarrage des conteneurs Docker
build:
	@docker compose up -d --build

lunch:
	@clear
	@docker compose down
	@docker compose up --build

# Linter
linter:
	@echo "=== Running backend tests ==="
	@pylint --rcfile=.pylintrc --fail-under=8 backend/code
	@echo "=== Running CDN tests ==="
	@pylint --rcfile=.pylintrc --fail-under=8 cdn/code
	@echo "=== All tests finished ==="

# Execute les tests unitaires
test_unitaires:
	@echo "=== Running backend tests ==="
	@pytest backend/tests/ -v
	# echo "=== Running CDN tests ==="
	# pytest cdn/tests/ -v
	@echo "=== All tests finished ==="