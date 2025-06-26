from flask import Flask, render_template, send_file, jsonify
import os
import subprocess
import sys
import time
import threading
from datetime import datetime

app = Flask(__name__)
VIDEO_DIR = os.path.join('static', 'videos')
OUTPUT_VIDEO = os.path.join(VIDEO_DIR, 'output', 'output34.mp4')
OUTPUT_VIDEO1 = os.path.join(VIDEO_DIR, 'output', 'output34_fixed.mp4')
INTRO_VIDEO = os.path.join(VIDEO_DIR, 'Intro1.mp4')
DELAY_SECONDS = 60 * 3  # 3 minutes

def run_python_files_sequentially(file_list_with_args):
    for file_entry in file_list_with_args:
        file_path = file_entry[0]
        args = file_entry[1] if len(file_entry) > 1 else []

        if not os.path.exists(file_path):
            print(f"🚫 Le fichier {file_path} n'existe pas. Ignoré.")
            continue
        if not file_path.endswith('.py'):
            print(f"⚠️ Le fichier {file_path} n'est pas un script Python. Ignoré.")
            continue

        print(f"\n▶️ Exécution de {file_path} avec arguments {args}...")
        try:
            result = subprocess.run([sys.executable, file_path] + args, check=True)
            print(f"✅ Fin de l'exécution de {file_path} (code {result.returncode})")
        except subprocess.CalledProcessError as e:
            print(f"❌ Erreur dans {file_path}: {e}")
        except Exception as e:
            print(f"❗ Erreur inattendue avec {file_path}: {e}")

def video_generation_loop():
    while True:
        try:
            print("\n🕒 Début du cycle de génération vidéo")

            # Suppression de l'ancienne vidéo avec vérification
            if os.path.exists(OUTPUT_VIDEO):
                try:
                    os.remove(OUTPUT_VIDEO)
                    print("🗑️ Ancienne vidéo supprimée")
                except Exception as e:
                    print(f"⚠️ Erreur suppression vidéo: {e}")
            
            if os.path.exists(OUTPUT_VIDEO1):
                try:
                    os.remove(OUTPUT_VIDEO1)
                    print("🗑️ Ancienne vidéo fixe supprimée")
                except Exception as e:
                    print(f"⚠️ Erreur suppression vidéo fixe: {e}")
            # Liste des scripts avec gestion des erreurs individuelles
            scripts = [
                ('scrapping_scripts/scrapping_actualite.py', []),
                ('scrapping_scripts/scrapping_indiceactions.py', []),
                ('scrapping_scripts/scrapping_vuemarche.py', []),
                ('scrapping_scripts/scrapping_palmares.py', []),
                ('scrapping_scripts/scrapping_devise.py', []),
                ('scrapping_scripts/scrapping_metal.py', []),
                ('video_generation2.py', [])
            ]

            # Exécution séquentielle avec gestion d'erreur
            for script in scripts:
                try:
                    run_python_files_sequentially([script])
                except Exception as e:
                    print(f"⚠️ Échec partiel: {script[0]} - {e}")
                    continue

            print(f"⏳ Prochaine exécution dans {DELAY_SECONDS//60} minutes")
            time.sleep(DELAY_SECONDS)

        except Exception as e:
            print(f"❗ Erreur majeure dans le cycle: {e}")
            print("🔄 Nouvelle tentative dans 30 secondes...")
            time.sleep(30)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video/')
def video():
    if os.path.exists(OUTPUT_VIDEO):
        return send_file(OUTPUT_VIDEO, mimetype='video/mp4')
    return send_file(INTRO_VIDEO, mimetype='video/mp4')

@app.route('/status/')
def status():
    exists = os.path.exists(OUTPUT_VIDEO)
    last_update = datetime.fromtimestamp(os.path.getmtime(OUTPUT_VIDEO)).strftime('%H:%M:%S') if exists else 'N/A'
    return jsonify({'video_exists': exists, 'last_update': last_update})

def start_video_generation_thread():
    thread = threading.Thread(target=video_generation_loop)
    thread.daemon = True  # Le thread s'arrêtera quand le main thread s'arrête
    thread.start()

if __name__ == '__main__':
    # Démarrer le thread de génération de vidéo
    start_video_generation_thread()
    
    # Démarrer le serveur Flask
    app.run(host='0.0.0.0', port=5043, debug=True)