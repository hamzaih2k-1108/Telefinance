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
    url = "https://www.cdgcapitalbourse.ma/trader/market/MA0000000050/XCAS/ISIN"
    driver.get(url)
    
    # Attendre le chargement
    time.sleep(5)
    
    # Récupérer le HTML
    html = driver.page_source
    
    # Parser avec BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # ==============================================
    # Scraping de la table "Dernières sessions" (table 1)
    # ==============================================
    tables = soup.find_all('table', {'class': 't-data-grid'})
    
    if len(tables) >= 1:
        # Table des dernières sessions (première table)
        table_sessions = tables[1]
        
        # Extraire les en-têtes
        headers_sessions = [th.get_text(strip=True) for th in table_sessions.find('thead').find_all('th')]
        
        # Extraire les données
        data_sessions = []
        for row in table_sessions.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            row_data = []
            for col in cols:
                text = col.get_text(strip=True)
                if any(c in text for c in [',', ' ']):
                    text = text.replace(' ', '').replace(',', '.')
                row_data.append(text)
            data_sessions.append(row_data)
            
        # Créer le DataFrame
        df_sessions = pd.DataFrame(data_sessions, columns=headers_sessions)
        
        # Sauvegarder en CSV
        df_sessions.to_csv('data_scrapped_csv/dernieres_sessions_MASI.csv', index=False, encoding='utf-8-sig')
        print("Fichier sauvegardé: dernieres_sessions_MASI.csv")
    
    # ==============================================
    # Scraping de la table "Indicateurs de marché" (table 2)
    # ==============================================
    if len(tables) >= 2:
        # Table des indicateurs de marché (deuxième table)
        table_indicateurs = tables[2]
        
        # Extraire les en-têtes
        headers_indicateurs = [th.get_text(strip=True) for th in table_indicateurs.find('thead').find_all('th')]
        
        # Extraire les données
        data_indicateurs = []
        for row in table_indicateurs.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            row_data = []
            for col in cols:
                text = col.get_text(strip=True)
                if any(c in text for c in [',', ' ']):
                    text = text.replace(' ', '').replace(',', '.')
                row_data.append(text)
            data_indicateurs.append(row_data)
            
        # Créer le DataFrame
        df_indicateurs = pd.DataFrame(data_indicateurs, columns=headers_indicateurs)
        
        # Sauvegarder en CSV
        df_indicateurs.to_csv('data_scrapped_csv/indicateurs_marche_MASI.csv', index=False, encoding='utf-8-sig')
        print("Fichier sauvegardé: indicateurs_marche_masi.csv")
    
    # Vérification si les tables ont été trouvées
    if len(tables) < 2:
        print(f"Attention: seulement {len(tables)} table(s) trouvée(s) sur 2 attendues")

    # Afficher un résumé
    print("\nRésumé du scraping:")
    if len(tables) >= 1:
        print(f"- Dernières sessions: {len(data_sessions)} lignes récupérées")
    if len(tables) >= 2:
        print(f"- Indicateurs de marché: {len(data_indicateurs)} lignes récupérées")

finally:
    # Fermer le navigateur
    driver.quit()