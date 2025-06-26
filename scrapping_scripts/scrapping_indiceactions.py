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
    url = "https://www.cdgcapitalbourse.ma/bourse/indicesaction"
    driver.get(url)
    
    # Attendre le chargement (meilleure pratique: utiliser WebDriverWait)
    time.sleep(5)
    
    # Récupérer le HTML
    html = driver.page_source
    
    # Parser avec BeautifulSoup
    soup = BeautifulSoup(html, 'html.parser')
    
    # Trouver le tableau
    table = soup.find_all('table', {'class': 't-data-grid'})[1] if len(soup.find_all('table', {'class': 't-data-grid'})) > 1 else None
    # Trouver la deuxième table avec la même classe
    table1 = soup.find_all('table', {'class': 't-data-grid'})[2] if len(soup.find_all('table', {'class': 't-data-grid'})) > 1 else None
    if table and table1:
        # Extraire les en-têtes
        headers = [th.get_text(strip=True) for th in table.find('thead').find_all('th')]
        headers1 = [th.get_text(strip=True) for th in table1.find('thead').find_all('th')]
        # Extraire les données
        data = []
        for row in table.find('tbody').find_all('tr'):
            cols = row.find_all('td')
            row_data = []
            for col in cols:
                text = col.get_text(strip=True)
                # Nettoyage avancé des nombres
                if any(c in text for c in [',', ' ']):
                    text = text.replace(' ', '').replace(',', '.')
                row_data.append(text)
            data.append(row_data)
        
        data1 = [] 
        for row in table1.find('tbody').find_all('tr'):
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
            data1.append(row_data)
                
        # Créer le DataFrame
        df = pd.DataFrame(data, columns=headers)
        df1 = pd.DataFrame(data1, columns=headers1)
        # Afficher les résultats
        print("Données indices/actions récupérées avec succès:")
        print(df.head(10))
        
        print("Données indices/actions-1- récupérées avec succès:")
        print(df1.head(10))       
        # Sauvegarder en CSV
        df.to_csv('data_scrapped_csv/indice_action.csv', index=False, encoding='utf-8-sig')
        print("\nFichier sauvegardé: indice_action.csv")
        df1.to_csv('data_scrapped_csv/indice_action-1-.csv', index=False, encoding='utf-8-sig')
        print("\nFichier sauvegardé: indice_action-1-.csv")
        
        
    else:
        print("Tableau non trouvé dans la page")

finally:
    # Fermer le navigateur
    driver.quit()