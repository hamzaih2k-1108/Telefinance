from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time

# Configuration de Selenium avec webdriver-manager
chrome_options = Options()
chrome_options.add_argument("--headless")  # Mode sans interface
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialisation automatique de ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

try:
    # Charger la page
    url = "https://www.cdgcapitalbourse.ma/bourse/vuemarche"
    driver.get(url)
    
    # Attendre le chargement (meilleure pratique: utiliser WebDriverWait)
    time.sleep(5)
    
    # Récupérer le HTML
    html = driver.page_source
    
    # Parser avec BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Trouver le tableau
    table = soup.find('table', {'id': 'instrument-search-table-STOCK'})
    
    if table:
        # Extraire les en-têtes
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        
        # Extraire les données
        data = [] 
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            row_data = []
            for col_idx, col in enumerate(cols):
                text = col.get_text(strip=True)
                # Appliquer le nettoyage avancé uniquement à la première colonne
                if col_idx == 0 and any(c in text for c in [',', ' ']):
                    text = text.replace(',', '.')
                else:
                    text = text.replace(' ', '').replace(',', '.')
                row_data.append(text)
            data.append(row_data)
        
        # Créer le DataFrame
        df = pd.DataFrame(data, columns=headers)
        
        # Nettoyage supplémentaire des données
        numeric_cols = ['PTO', 'PTC', 'Cours', 'Var.(%)', 'CMP', 'Ouverture', '+ Haut', '+ Bas', 'Volume']
        for col in numeric_cols:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Afficher les résultaÒÒts
        print("Données boursières récupérées avec succès:")
        print(df.head(10))
        
        # Sauvegarder en CSV
        df.to_csv('data_scrapped_csv/marche_boursier_maroc.csv', index=False, encoding='utf-8-sig')
        print("\nFichier sauvegardé: marche_boursier_maroc.csv")
        
    else:
        print("Tableau non trouvé dans la page")

finally:
    # Fermer le navigateur
    driver.quit()