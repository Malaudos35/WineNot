.PHONY: all venv build test_unitaires scan_images_local install_githooks

TRIVY_IMAGE ?= aquasec/trivy:0.61.1
LOCAL_IMAGES ?= winenot-backend:latest winenot-frontend:latest

# Cible par défaut : affiche les commandes sans les exécuter
default:
	@echo "Commandes disponibles :"
	@echo "  make all            - Exécute toutes les commandes"
	@echo "  make venv           - Crée l'environnement virtuel et installe les dépendances"
	@echo "  make build          - Construit et lance les conteneurs Docker en arriere plan"
	@echo "  make lunch          - Construit et lance les conteneurs Docker en interactif"
	@echo "  make linter         - Lance le linter sur le code python"
	@echo "  make test_unitaires - Exécute les tests unitaires"
	@echo "  make scan_images_local - Build et scan Trivy des images locales"
	@echo "  make install_githooks  - Active le hook pre-push local"

# Cible pour tout exécuter
all: venv build test_unitaires

# Crée et active un environnement virtuel, puis installe les dépendances
venv:
	@python -m venv venv
	@. venv/bin/activate && pip install -r backend/requirements.txt

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
	@echo "=== All tests finished ==="

# Execute les tests unitaires
test_unitaires:
	@echo "=== Running backend tests ==="
	@pytest backend/tests/ -v
	@echo "=== All tests finished ==="

scan_images_local:
	@echo "[scan] Building local images before security scan..."
	@docker compose build backend frontend
	@echo "[scan] Scanning images with Trivy (HIGH,CRITICAL)..."
	@for image in $(LOCAL_IMAGES); do \
		if ! docker image inspect $$image >/dev/null 2>&1; then \
			echo "ERROR: image '$$image' not found after build."; \
			exit 1; \
		fi; \
		echo "[scan] $$image"; \
		docker run --rm \
			-v /var/run/docker.sock:/var/run/docker.sock \
			$(TRIVY_IMAGE) image \
			--severity HIGH,CRITICAL \
			--ignore-unfixed \
			--exit-code 1 \
			--no-progress \
			$$image; \
	done
	@echo "[scan] Security scan passed for all local images."

install_githooks:
	@chmod +x ./.githooks/pre-push
	@git config core.hooksPath .githooks
	@echo "Git hook pre-push active via .githooks/pre-push"