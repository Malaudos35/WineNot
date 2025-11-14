from playwright.sync_api import sync_playwright
import re
# import requests
import json
import time
import random

# Liste de User-Agents pour simuler différents navigateurs
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.4 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

def scrape_vivino_info(query):
    with sync_playwright() as p:
        # Lancer un navigateur (Chromium en mode headless)
        browser = p.chromium.launch(
            headless=True,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--disable-infobars',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
            ]
        )

        # Sélection aléatoire d'un User-Agent
        user_agent = random.choice(USER_AGENTS)

        # Configurer le contexte du navigateur avec les headers choisis
        context = browser.new_context(
            user_agent=user_agent,
            java_script_enabled=True,
            ignore_https_errors=True,
            locale='fr-FR',
            viewport={'width': 1920, 'height': 1080},
        )

        page = context.new_page()

        try:
            # 1. Accéder à la page de recherche Vivino
            search_url = f"https://www.vivino.com/fr/search/wines?q={query.replace(' ', '+')}"
            print(f"Recherche de '{query}' sur Vivino...")
            page.goto(search_url, timeout=60000)

            # Simuler un comportement humain : défilement aléatoire
            page.evaluate("window.scrollBy(0, 200)")
            time.sleep(random.uniform(1, 3))

            # 2. Trouver le premier lien vers un vin
            first_wine_link = page.query_selector("a[href*='/w/']")
            if not first_wine_link:
                print("Aucun résultat trouvé pour ce vin.")
                return False

            wine_url = "https://www.vivino.com" + str(first_wine_link.get_attribute("href"))
            print(f"Accès à la page du vin : {wine_url}")

            # 3. Accéder à la page du vin
            page.goto(wine_url, timeout=60000)

            # Simuler un comportement humain : défilement aléatoire
            page.evaluate("window.scrollBy(0, 300)")
            time.sleep(random.uniform(1, 3))

            # Récupérer le titre du vin
            title_element = page.query_selector(".wineHeadline-module__wineHeadline--32Ety")
            title = title_element.inner_text() if title_element else "Non disponible"

            # Récupérer le prix
            price_element = page.query_selector(".purchaseAvailability__currentPrice--3mO4u")
            price = price_element.inner_text() if price_element else "Non disponible"

            # Récupérer les informations du vignoble
            wine_facts = {}
            wine_facts_rows = page.query_selector_all("tr[data-testid='wineFactRow']")
            for row in wine_facts_rows:
                header = row.query_selector(".wineFacts__headerLabel--14doB")
                fact = row.query_selector(".wineFacts__fact--3BAsi")
                if header and fact:
                    header_text = header.inner_text().strip()
                    fact_text = fact.inner_text().strip()
                    wine_facts[header_text] = fact_text

            # Récupérer la description du vin
            description_element = page.query_selector("td.wineFacts__fact--3BAsi span:last-child")
            description = description_element.inner_text() if description_element else "Non disponible"

            # 4. Récupérer toutes les images et trouver celle avec la plus haute résolution
            html_content = page.content()

            # Utiliser une regex pour trouver toutes les URLs d'images
            srcset_matches = re.findall(r'srcset=["\']([^"\']+)["\']', html_content)
            src_matches = re.findall(r'src=["\']([^"\']+)["\']', html_content)

            # Combiner les résultats
            all_image_urls = []
            for match in srcset_matches:
                urls = [url.strip() for url in match.split(',')]
                all_image_urls.extend(urls)
            all_image_urls.extend(src_matches)

            # Filtrer les URLs uniques et compléter avec https:
            unique_image_urls = list(set(all_image_urls))
            complete_image_urls = ["https:" + url if url.startswith("//") else url for url in unique_image_urls]

            # Filtrer les URLs pour ne garder que celles de Vivino
            vivino_image_urls = [url for url in complete_image_urls if "images.vivino.com" in url]

            if not vivino_image_urls:
                print("Aucune image Vivino trouvée.")
                return False

            # Trouver l'image avec la plus haute résolution (celle avec _x960 ou _x1200)
            highest_resolution_url = None
            for url in vivino_image_urls:
                url = url.split(" ")[0]
                if "_x960." in url:
                    highest_resolution_url = url
                    break
                elif "_x1200." in url:
                    highest_resolution_url = url
                    break
            else:
                # Si aucune image haute résolution n'est trouvée, prendre la première
                highest_resolution_url = vivino_image_urls[0]

            # Retourner un JSON avec toutes les informations
            result = {
                "title": title,
                "price": price,
                "wine_facts": wine_facts,
                "description": description,
                "image_url": highest_resolution_url
            }

            return result

        except Exception as e:
            print(f"Erreur : {e}")
            return False

if __name__ == "__main__":
    result = scrape_vivino_info("Petrus 1987")
    if result:
        with open("vin_info.json", "w", encoding="utf-8") as f:
            json.dump(result, f, ensure_ascii=False, indent=4)
        print("Les informations ont été sauvegardées dans vin_info.json")
    else:
        print("Aucune information n'a pu être récupérée.")
