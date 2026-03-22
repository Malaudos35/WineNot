FROM mcr.microsoft.com/playwright:v1.56.0

# Forcer l'installation de Playwright v1.56.0
RUN npm install -g playwright@1.56.0

# Lancer le serveur Playwright
CMD ["npx", "playwright", "run-server", "--port=3000", "--host=0.0.0.0"]
