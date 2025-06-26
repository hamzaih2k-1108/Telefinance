from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import pandas as pd
import time
from urllib.parse import urljoin
import requests
import os

# Configuration de Selenium
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# Initialisation automatique de ChromeDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service, options=chrome_options)

def get_article_details(base_url, relative_url):
    """Fonction pour récupérer les détails d'un article (intro, image et légende)"""
    full_url = urljoin(base_url, relative_url)
    details = {'Intro': None, 'Image': None, 'Légende': None}
    
    try:
        driver.get(full_url)
        time.sleep(2)  # Attente courte pour le chargement
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        
        # Récupérer l'intro
        intro = soup.find('p', class_='intro')
        details['Intro'] = intro.get_text(strip=True) if intro else None
        
        
        reference_div = soup.find('div', class_='reference-left')
        if reference_div:
            img = reference_div.find('img')
            if img and 'src' in img.attrs:
                details['Image'] = urljoin(base_url, img['src'])
                # Récupérer la légende
                legend = reference_div.find('p', class_='reference-title')
                details['Légende'] = legend.get_text(strip=True) if legend else None
                # Télécharger l'image
                download_image(details['Image'])
            
    except Exception as e:
        print(f"Erreur lors de la récupération de {full_url}: {str(e)}")
    
    return details

def download_image(image_url):
    """Fonction pour télécharger l'image"""
    try:
        response = requests.get(image_url)
        if response.status_code == 200:
            # Créer un dossier pour les images si nécessaire
            if not os.path.exists('images_actualite'):
                os.makedirs('images_actualite')
            # Extraire le nom de l'image
            image_name = os.path.join('images_actualite', image_url.split('/')[-1])
            with open(image_name, 'wb') as file:
                file.write(response.content)
            return image_name
    except Exception as e:
        print(f"Erreur lors du téléchargement de l'image: {str(e)}")
    return None

try:
    # Charger la page des actualités
    base_url = "https://www.cdgcapitalbourse.ma"
    url = f"{base_url}/market/allmarketactualites"
    driver.get(url)
    
    # Attendre le chargement
    time.sleep(5)
    
    # Récupérer le HTML
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    
    # Trouver la liste des actualités
    news_list = soup.find('dl', class_='news-list')
    
    if news_list:
        # Initialiser les listes pour stocker les données
        data = []
        
        # Parcourir les paires dt/dd
        for dt, dd in zip(news_list.find_all('dt', class_='dateTime'),
                          news_list.find_all('dd', class_='titleDoc')):
            
            # Extraire les données de base
            date_heure = dt.get_text(strip=True)
            link = dd.find('a')
            if link:
                relative_url = link['href']
                titre = link.get_text(strip=True)
                
                # Récupérer les détails supplémentaires
                details = get_article_details(base_url, relative_url)
                
                data.append({
                    'Date & Heure': date_heure,
                    'Titre': titre,
                    'Lien': urljoin(base_url, relative_url),
                    'Intro': details['Intro'],
                    'URL Image': details['Image'],
                    'Légende Image': details['Légende']
                })
        
        # Créer le DataFrame
        df = pd.DataFrame(data)
        
        # Convertir la colonne Date & Heure en datetime
        df['Date & Heure'] = pd.to_datetime(df['Date & Heure'], format='%d/%m/%Y %H:%M')
        
        # Afficher les résultats
        print("Actualités récupérées avec succès:")
        print(df.head())
        
        # Sauvegarder en CSV
        df.to_csv('data_scrapped_csv/actualites_boursieres_completes.csv', index=False, encoding='utf-8-sig')
        print("\nFichier sauvegardé: actualites_boursieres_completes.csv")
        
    else:
        print("Liste d'actualités non trouvée dans la page")

finally:
    # Fermer le navigateur
    driver.quit()