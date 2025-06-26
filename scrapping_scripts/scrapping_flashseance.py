from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

# Base URL préfixée
base_href = "https://www.cdgcapitalbourse.ma"
listing_url = "https://www.cdgcapitalbourse.ma/market/allmarketactualites"

all_data = []

try:
    # Étape 1 : Charger la page de liste des actualités
    driver.get(listing_url)
    time.sleep(4)
    soup = BeautifulSoup(driver.page_source, "html.parser")

    # Étape 2 : Trouver tous les liens <a> dans les blocs .une
    hrefs = []
    une = soup.find("div", class_="une")
    unes = une.find("ul", class_="links-list")
    a_tag = unes.find("a", href=True)
    if a_tag:
        print(a_tag["href"])
        full_url = urljoin(base_href, a_tag["href"])
        hrefs.append(full_url)
        print(f"🔗 Lien trouvé : {full_url}")
    else:
        print("⚠️ Aucun lien trouvé dans la liste des actualités.")

    # Étape 3 : Parcourir chaque lien et extraire les infos
    for url in hrefs:
        print(f"🔍 Traitement de : {url}")
        try:
            driver.get(url)
            time.sleep(4)
            detail_soup = BeautifulSoup(driver.page_source, "html.parser")

            # Date
            date_tag = detail_soup.find("p", class_="popupStatus")
            date_actualite = date_tag.get_text(strip=True) if date_tag else "Non précisée"

            # Paragraphes
            news_body = detail_soup.find("div", id="newsBody")
            paragraphs = news_body.find_all("p") if news_body else []

            for p in paragraphs:
                texte = p.get_text(separator=" ", strip=True)
                if texte:
                    all_data.append({
                        "date_actualite": date_actualite,
                        "texte": texte,
                        "url": url
                    })

        except Exception as e:
            print(f"⚠️ Erreur pour {url} : {e}")

    # Étape 4 : Export CSV
    df = pd.DataFrame(all_data)
    df.to_csv("flash_seance.csv", index=False, encoding="utf-8-sig")
    print("✅ Données enregistrées dans flash_seance.csv")

finally:
    driver.quit()
