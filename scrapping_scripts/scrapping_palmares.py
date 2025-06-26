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
    # ==============================================
    # Scraping de la table À la hausse" (table 1)
    # ==============================================
    
    # Charger la page
    url = "https://www.cdgcapitalbourse.ma/bourse/palmaresaction"
    driver.get(url)
    
    # Attendre le chargement
    time.sleep(5)
    
    # Récupérer le HTML
    html = driver.page_source
    
    # Parser avec BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
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
                    text = text.replace(',', '.')
                row_data.append(text)
            data_sessions.append(row_data)
            
        # Créer le DataFrame
        df_sessions = pd.DataFrame(data_sessions, columns=headers_sessions)
        
        # Sauvegarder en CSV
        df_sessions.to_csv('data_scrapped_csv/hausse_indices.csv', index=False, encoding='utf-8-sig')
        print("Fichier sauvegardé: hausse_indices.csv")
    
    
    # ==============================================
    # Scraping de la table À la baisse" (table 2)
    # ==============================================
    
    # Charger la page
    url1 = "https://www.cdgcapitalbourse.ma/bourse/palmaresaction/MASI/DOWN/DAY_1"
    driver.get(url1)
    
    # Attendre le chargement
    time.sleep(2)
    
    # Récupérer le HTML
    html1 = driver.page_source
    
    # Parser avec BeautifulSoup
    soup1 = BeautifulSoup(html1, 'html.parser')
    tables1 = soup1.find_all('table', {'class': 't-data-grid'})
    
    if len(tables1) >= 0:
        # Table des dernières sessions (première table)
        table_sessions1 = tables1[1]
        
        # Extraire les en-têtes
        headers_sessions1 = [th.get_text(strip=True) for th in table_sessions1.find('thead').find_all('th')]
        
        # Extraire les données
        data_sessions1 = []
        for row in table_sessions1.find('tbody').find_all('tr'):
            cols1 = row.find_all('td')
            row_data1 = []
            for col in cols1:
                text1 = col.get_text(strip=True)
                if any(c in text1 for c in [',', ' ']):
                    text1 = text1.replace(',', '.')
                row_data1.append(text1)
            data_sessions1.append(row_data1)
            
        # Créer le DataFrame
        df_sessions1 = pd.DataFrame(data_sessions1, columns=headers_sessions1)
        
        # Sauvegarder en CSV
        df_sessions1.to_csv('data_scrapped_csv/baisses_indices.csv', index=False, encoding='utf-8-sig')
        print("Fichier sauvegardé: baisses_indices.csv")
        
finally:
    # Fermer le navigateur
    driver.quit()