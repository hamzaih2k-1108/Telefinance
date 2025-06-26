from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")  # Mode sans interface
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialisation du WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Charger la page
    url = "https://www.cdgcapitalbourse.ma/#"
    driver.get(url)

    # Attendre le chargement
    time.sleep(5)

    # Récupérer le HTML
    html = driver.page_source

    # Parser avec BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')

    # Trouver le div principal contenant les données optionnelles
    optional_data_div = soup.find('div', id='optional-data')

    if optional_data_div:
        # Récupérer tous les blocs info level2
        info_blocks = optional_data_div.find_all('div', class_='info level2')
        
        if len(info_blocks) >= 2:
            metals_div = info_blocks[1]  # Le deuxième bloc contient les métaux précieux
            
            # Chercher le tableau à l'intérieur
            table = metals_div.find('table')
            
            if table:
                # Extraire les données
                data = []
                for row in table.find_all('tr'):
                    cols = row.find_all(['th', 'td'])
                    row_data = [col.get_text(strip=True).replace('\xa0', ' ') for col in cols]
                    data.append(row_data)

                # Créer le DataFrame
                df = pd.DataFrame(data[1:], columns=data[0])

                # Affichage
                print("✅ Données des métaux précieux récupérées :")
                print(df)

                # Sauvegarde
                df.to_csv('data_scrapped_csv/metaux_precieux.csv', index=False, encoding='utf-8-sig')
                print("\n💾 Fichier sauvegardé : metaux_precieux.csv")

            else:
                print("❌ Tableau introuvable dans le deuxième bloc 'info level2'.")
        else:
            print("❌ Moins de deux blocs 'info level2' trouvés.")
    else:
        print("❌ Bloc 'optional-data' introuvable.")

finally:
    driver.quit()
