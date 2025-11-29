# Étape 1 : Construire l'environnement avec les dépendances
FROM python:3.11-slim as builder

WORKDIR /tmp

ENV DEBIAN_FRONTEND=noninteractive

# Installer les dépendances système et Node.js
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    curl \
    ca-certificates \
    tzdata \
    wget \
    gnupg \
    libnss3 \
    libnspr4 \
    libdbus-1-3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libxcursor1 \
    libgtk-3-0 \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && \
    rm -rf /var/lib/apt/lists/*

# Installer les dépendances Python et Playwright
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt
RUN npx playwright install --with-deps >> /dev/null

# Étape 2 : Créer l'image finale légère (sans Node.js)
FROM python:3.11-slim

WORKDIR /app

RUN useradd -m appuser

# Copier les navigateurs Playwright et les dépendances Python
COPY --from=builder /root/.local /home/appuser/.local
COPY --from=builder /root/.cache/ms-playwright /root/.cache/ms-playwright
COPY --from=builder /tmp/requirements.txt .
COPY . .

ENV PATH=/home/appuser/.local/bin:$PATH
ENV PLAYWRIGHT_BROWSERS_PATH=/root/.cache/ms-playwright

RUN chown -R appuser:appuser /app
RUN chown -R appuser:appuser /home/appuser/.local

USER appuser

EXPOSE 5000

CMD ["uvicorn", "main:app", "--reload", "--port", "5000", "--host", "0.0.0.0"]
