import cv2
import numpy as np
import pandas as pd
from PIL import Image, ImageDraw, ImageFont, ImageSequence
import os
import subprocess
import locale
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime
import math
import traceback


locale.setlocale(locale.LC_TIME, 'fr_FR.UTF-8') 

class NewsTemplateGenerator:
    def __init__(self):
        self.settings = {
            
            'csv_path': 'data_scrapped_csv/actualites_boursieres_completes.csv',
            'market_data_path': 'data_scrapped_csv/marche_boursier_maroc.csv',  
            'MASI_indicateurs_path': 'data_scrapped_csv/indicateurs_marche_MASI.csv',
            'derniere_sessions_path': 'data_scrapped_csv/dernieres_sessions_MASI.csv',
            'image_folder': 'images_actualite',
            'audio_path': 'video_components/news_sound.mp3',
            'background_gif_path': 'video_components/breakiing.jpg',
            'output_video': 'static/videos/output/output34_fixed.mp4', 
            'fleche_verte_path': 'video_components/fleche_vert.png',
            'fleche_rouge_path': 'video_components/fleche_rouge.png',
            'slide_duration': 9,
            'fps': 15,  #15
            'resolution': (1280, 720),
            'font': 'Verdana.ttf',  #Segoe UI
            'font_ticker': 'video_components/fonts/Verdana-Bold.ttf',
            'font_bold': 'video_components/fonts/Verdana-Bold.ttf',
            'font_date':'video_components/fonts/Verdana-Bold.ttf',
            'title_size': 37,
            'intro_size': 22,
            'MASI_size': 16,
            'ticker_size': 16, 
            'date_size': 20,
            'table_font_size': 14, 
            'metal_font_size': 12,
            'ticker_positive_color': (25,137,79),
            'ticker_negative_color': (236,33,39),
            'table_positive_color': (0,0,0),
            'table_negative_color': (0,0,0),
            'ticker_neutral_color': (0, 0, 0),
            'title_color': (0, 0, 0),
            'intro_color': (0, 0, 0),
            'table_header_color_kpi_masi': (255, 80, 0), # Second Option Orange
            'table_header_color': (0, 0, 0),# Orange
            'table_header_colorr': (0, 0, 0),  # Noir
            'titre_masi_KPI' : (0, 0, 0),
            'table_text_color': (0, 0, 0),  # Noir
            'table_segment_text_color': (0, 0, 0),
            'title_intro_spacing': 30,
            'ticker_data_path': "data_scrapped_csv/indice_action-1-.csv",
            'title_max_width': 520,
            'intro_max_width': 520,
            'image_max_width': 500,
            'image_max_height': 390,
            'title_max_height': 150,
            'intro_max_height': 250,
            'ticker_y_position': 680,
            'table_rows_per_block': 3,  # 3 lignes par bloc
            'table_blocks': 3,  # 3 blocs
            'table_start_x': 70,
            'table_start_y': 558,
            'table_col_spacing': 130,
            'table_row_spacing': 25,
            'table_min_col_spacing': 4,  # Espace minimum entre colonnes
            'table_block_spacing': 40,    # Espace entre blocs
        }

        try:
            self.font_title = ImageFont.truetype(self.settings['font_bold'], self.settings['title_size'])
            self.font_intro = ImageFont.truetype(self.settings['font'], self.settings['intro_size'])
            self.font_ticker = ImageFont.truetype(self.settings['font_ticker'], self.settings['ticker_size'])
            self.font_date = ImageFont.truetype(self.settings['font_date'], self.settings['date_size'])
            self.font_table = ImageFont.truetype(self.settings['font'], self.settings['metal_font_size'])
            self.font_table_bold = ImageFont.truetype(self.settings['font_bold'], self.settings['metal_font_size'])
            self.font_metal_bold = ImageFont.truetype(self.settings['font'], self.settings['metal_font_size'])
            self.font_libelle_palmares = ImageFont.truetype(self.settings['font'], 10)
        except OSError:
            print("⚠️ Impossible de charger la police, police par défaut utilisée.")
            self.font_title = ImageFont.load_default()
            self.font_intro = ImageFont.load_default()
            self.font_ticker = ImageFont.load_default()

        self.background_gif = Image.open(self.settings['background_gif_path'])
        self.gif_frames = [frame.convert("RGBA").resize(self.settings['resolution']) for frame in ImageSequence.Iterator(self.background_gif)]
        self.current_gif_frame = 0
        self.ticker_data = self.load_ticker_data()
        self.market_data = self.load_market_data()
        self.ticker_segments = self.prepare_ticker_segments()
        self.current_table_offset = 0

    def load_ticker_data(self):
        try:
            df = pd.read_csv(self.settings['ticker_data_path'])
            df = df[['Libellé', 'Cours', 'Var % 31/12']].dropna()
            # print(len(df), "tickers chargés")
            return df
        except Exception as e:
            print(f"⚠️ Erreur chargement ticker: {e}")
            return pd.DataFrame()

    def load_market_data(self):
        try:
            df = pd.read_csv(self.settings['market_data_path'])
            df = df[['Libellé', 'Cours', 'Var.(%)']].dropna()
            # print(len(df), "données marché chargées")
            return df
        except Exception as e:
            print(f"⚠️ Erreur chargement données marché: {e}")
            return pd.DataFrame()

    def prepare_ticker_segments(self):
        segments = []
        if not self.ticker_data.empty:
            for _, row in self.ticker_data.iterrows():
                libelle = str(row['Libellé'])
                cours = str(row['Cours'])
                var = str(row['Var % 31/12'])
                try:
                    var_value = float(var.replace('%', '').strip())
                    if var_value > 0:
                        color = self.settings['ticker_positive_color']
                    elif var_value < 0:
                        color = self.settings['ticker_negative_color']
                    else:
                        color = self.settings['ticker_neutral_color']
                except:
                    color = self.settings['ticker_neutral_color']
                segments.append({ 'text': f"{libelle}: {cours}MAD {var}%", 'color': color, 'width': None })
        spaced_segments = []
        for segment in segments:
            if spaced_segments:
                spaced_segments.append({'text': "   ", 'color': (0, 0, 0), 'width': None})
            spaced_segments.append(segment)
        return spaced_segments

    def draw_text_block(self, image, text, position, font, max_width, color, max_height=None):
        draw = ImageDraw.Draw(image)
        words = text.split()
        lines = []
        current_line = []
        y = position[1]
        for word in words:
            test_line = ' '.join(current_line + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font)
            w = bbox[2] - bbox[0]
            if w < max_width:
                current_line.append(word)
            else:
                lines.append(' '.join(current_line))
                current_line = [word]
        if current_line:
            lines.append(' '.join(current_line))

        for line in lines:
            line_height = draw.textbbox((0, 0), line, font=font)[3] - draw.textbbox((0, 0), line, font=font)[1]
            if max_height is not None and (y + line_height) > (position[1] + max_height):
                break
            draw.text((position[0], y), line, font=font, fill=color)
            y += line_height + 5
        
        return y

    def create_title_frame(self, title):
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        final_y = self.draw_text_block(
            img, title, (130, 120), self.font_title, 
            self.settings['title_max_width'], self.settings['title_color'],
            self.settings['title_max_height']
        )
        return img, final_y

    def create_intro_frame(self, intro, title_final_y):
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        intro_y = title_final_y + self.settings['title_intro_spacing']
        self.draw_text_block(
            img, intro, (130, intro_y), self.font_intro,
            self.settings['intro_max_width'], self.settings['intro_color'],
            self.settings['intro_max_height']
        )
        return img

    def create_image_frame(self, image_path):
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        if image_path and os.path.exists(image_path):
            news_img = Image.open(image_path).convert("RGBA")
            news_img.thumbnail((self.settings['image_max_width'], self.settings['image_max_height']))
            paste_x = 750 + (self.settings['image_max_width'] - news_img.width) // 2
            paste_y = 90 + (self.settings['image_max_height'] - news_img.height) // 2
            img.paste(news_img, (paste_x, paste_y))
        return img

    def create_market_table_frame(self):
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        if self.market_data.empty:
            return img

        # Charger les images des flèches
        try:
            arrow_up = Image.open(self.settings['fleche_verte_path']).convert("RGBA")
            arrow_down = Image.open(self.settings["fleche_rouge_path"]).convert("RGBA")
            # Redimensionner les flèches si nécessaire (par exemple 12x12 pixels)
            arrow_size = (13, 13)
            arrow_up = arrow_up.resize(arrow_size)
            arrow_down = arrow_down.resize(arrow_size)
        except Exception as e:
            print(f"⚠️ Erreur chargement des flèches: {e}")
            arrow_up = None
            arrow_down = None

        rows_per_block = self.settings['table_rows_per_block']
        blocks = self.settings['table_blocks']
        total_rows = len(self.market_data)
        start_idx = self.current_table_offset % max(1, total_rows - rows_per_block * blocks + 1)
        
        # Vérifier si un libellé dépasse 8 caractères
        reduce_font = False
        for block in range(blocks):
            for row in range(rows_per_block):
                idx = start_idx + block * rows_per_block + row
                if idx >= total_rows:
                    continue
                libelle = str(self.market_data.iloc[idx]['Libellé'])
                if len(libelle) > 8:
                    reduce_font = True
                    break
            if reduce_font:
                break
        
        # Ajuster la police si nécessaire
        current_font_size = self.settings['table_font_size'] - 2 if reduce_font else self.settings['table_font_size']
        try:
            font_table = ImageFont.truetype(self.settings['font'], current_font_size)
        except:
            font_table = ImageFont.load_default()

        # Calculer la largeur maximale des libellés pour chaque bloc
        max_libelle_widths = [0] * blocks
        for block in range(blocks):
            for row in range(rows_per_block):
                idx = start_idx + block * rows_per_block + row
                if idx >= total_rows:
                    continue
                libelle = str(self.market_data.iloc[idx]['Libellé'])
                width = draw.textlength(libelle, font=font_table)
                if width > max_libelle_widths[block]:
                    max_libelle_widths[block] = width

        # Dessiner les en-têtes
        headers = ["Libellé", "Cours", "Var"]
        for block in range(blocks):
            # Calcul du décalage horizontal du bloc avec plus d'espace entre les blocs
            block_offset = sum(max_libelle_widths[:block]) + block * (self.settings['table_col_spacing'] * 2 + 50)  # Ajout de 100px entre les blocs
            
            # Affichage des headers pour chaque bloc
            x_libelle = self.settings['table_start_x'] + block_offset
            draw.text((x_libelle, self.settings['table_start_y']), headers[0], 
                    font=self.font_table_bold, fill=self.settings['table_header_color'])
            
            # Réduire l'espace entre Cours et Var (de 20 à 10)
            x_cours = x_libelle + max_libelle_widths[block] + 20  # Réduit de 20 à 10
            draw.text((x_cours, self.settings['table_start_y']), headers[1], 
                    font=self.font_table_bold, fill=self.settings['table_header_color'])
            
            # Réduire l'espace après Cours (de table_col_spacing à 40)
            x_var = x_cours + 100  # Réduit l'espacement après Cours
            draw.text((x_var, self.settings['table_start_y']), headers[2], 
                    font=self.font_table_bold, fill=self.settings['table_header_color'])
        
        # Dessiner les données
        for block in range(blocks):
            # Ajouter un espacement plus important entre les blocs (100px)
            block_offset = sum(max_libelle_widths[:block]) + block * (self.settings['table_col_spacing'] * 2 + 50)
            
            for row in range(rows_per_block):
                idx = start_idx + block * rows_per_block + row
                if idx >= total_rows:
                    break
                
                data = self.market_data.iloc[idx]
                libelle = str(data['Libellé'])
                cours = str(data['Cours'])
                var = str(data['Var.(%)'])
                
                # Position Y de la ligne
                y_row = self.settings['table_start_y'] + (row + 1) * self.settings['table_row_spacing']
                
                # Position X des colonnes
                x_libelle = self.settings['table_start_x'] + block_offset
                x_cours = x_libelle + max_libelle_widths[block] + 20  # Espace réduit après Libellé
                x_var = x_cours + 100  # Espace réduit après Cours
                
                # Dessiner les cellules
                draw.text((x_libelle, y_row), libelle, font=font_table, fill=self.settings['table_segment_text_color'])
                draw.text((x_cours, y_row), cours, font=font_table, fill=self.settings['table_segment_text_color'])
                
                # Déterminer la couleur et la flèche en fonction de la variation
                try:
                    var_value = float(var.strip())
                    if var_value > 0:
                        var_color = self.settings['table_positive_color']
                        arrow = arrow_up
                    else:
                        var_color = self.settings['table_negative_color']
                        arrow = arrow_down
                except:
                    var_color = self.settings['table_text_color']
                    arrow = None
                
                # Dessiner la flèche avant la valeur si disponible
                if arrow:
                    # Convertir les coordonnées en entiers
                    arrow_x = int(x_var)
                    arrow_y = int(y_row)
                    img.paste(arrow, (arrow_x, arrow_y), arrow)
                    # Ajuster la position du texte pour laisser de la place à la flèche
                    draw.text((arrow_x + 15, arrow_y), var, font=font_table, fill=var_color)
                else:
                    draw.text((int(x_var), int(y_row)), var, font=font_table, fill=var_color)
        
        # Incrémenter pour l'animation
        frames_per_table_slide = self.settings['fps'] * 10
        if self.total_frame_count % frames_per_table_slide == 0:
            self.current_table_offset += self.settings['table_rows_per_block'] * self.settings['table_blocks']
            if self.current_table_offset >= len(self.market_data):
                self.current_table_offset = 0
                    
        return img

    def create_ticker_frame(self, frame_idx):
        full_img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        draw = ImageDraw.Draw(full_img)

        # Charger les flèches
        try:
            arrow_up = Image.open(self.settings["fleche_verte_path"]).convert("RGBA").resize((12, 16))
            arrow_down = Image.open(self.settings["fleche_rouge_path"]).convert("RGBA").resize((12, 16))
        except Exception as e:
            print(f"⚠️ Erreur chargement des flèches: {e}")
            arrow_up = arrow_down = None

        # Charger police en gras si disponible
        try:
            font_bold = self.font_ticker
        except:
            font_bold = self.font_ticker  # fallback

        # Calcul des largeurs si pas encore fait
        if any(seg['width'] is None for seg in self.ticker_segments):
            for seg in self.ticker_segments:
                seg['width'] = draw.textlength(seg['text'], font=font_bold)

        total_width = sum(seg['width'] for seg in self.ticker_segments)
        speed_px_per_frame = 8
        offset = self.settings['resolution'][0] - (frame_idx * speed_px_per_frame) % (total_width + 100)
        y = self.settings['ticker_y_position']
        current_x = offset

        ticker_img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        ticker_draw = ImageDraw.Draw(ticker_img)

        for seg in self.ticker_segments * 2:
            if current_x + seg['width'] < 0:
                current_x += seg['width']
                continue
            if current_x > self.settings['resolution'][0]:
                break

            # Traitement du texte formaté : "Libellé: Cours Var%"
            text_parts = seg['text'].split()
            if len(text_parts) >= 3 and ':' in seg['text']:
                try:
                    colon_index = seg['text'].index(':')
                    libelle = seg['text'][:colon_index+1]
                    remaining = seg['text'][colon_index+1:].strip().split()

                    cours = remaining[0]
                    var = remaining[1]

                    # Libellé
                    ticker_draw.text((current_x, y), libelle, font=font_bold, fill=(0, 0, 0))
                    current_x += draw.textlength(libelle, font=font_bold) + 5

                    # Cours
                    ticker_draw.text((current_x, y), cours, font=font_bold, fill=(0, 0, 0))
                    current_x += draw.textlength(cours, font=font_bold) + 5

                    # Variation + flèche
                    var_value = float(var.replace('%', '').replace(',', '.'))
                    arrow = arrow_up if var_value > 0 else arrow_down
                    var_color = self.settings['ticker_positive_color'] if var_value > 0 else self.settings['ticker_negative_color']

                    if arrow:
                        arrow_y = y + (self.font_ticker.size - 12) // 2
                        ticker_img.paste(arrow, (int(current_x), int(arrow_y)), arrow)
                        current_x += 15

                    ticker_draw.text((current_x, y), var, font=font_bold, fill=var_color)
                    current_x += draw.textlength(var, font=font_bold) + 20

                    # Séparateur
                    separator = "   •   "
                    ticker_draw.text((current_x, y), separator, font=font_bold, fill=(0, 0, 0))
                    current_x += draw.textlength(separator, font=font_bold)

                except Exception as e:
                    print(f"⚠️ Erreur format variation: {e}")
                    ticker_draw.text((current_x, y), seg['text'], font=font_bold, fill=seg['color'])
                    current_x += seg['width']
            else:
                # Texte brut (format non reconnu)
                ticker_draw.text((current_x, y), seg['text'], font=font_bold, fill=seg['color'])
                current_x += seg['width']

        # Masque pour afficher uniquement la zone du ticker
        mask = Image.new("L", self.settings['resolution'], 0)
        mask_draw = ImageDraw.Draw(mask)
        visible_x_start = 185
        visible_x_end = 1280
        visible_y_start = y - 7
        visible_y_end = y + font_bold.size + 7
        mask_draw.rectangle([visible_x_start, visible_y_start, visible_x_end, visible_y_end], fill=255)

        full_img = Image.composite(ticker_img, full_img, mask)
        return full_img

    
    def draw_datetime_block(self, image, datetime_str):
        try:
            date = pd.to_datetime(datetime_str)
            formatted = date.strftime("%d %B %Y")
        except Exception:
            formatted = str(datetime_str)

        draw = ImageDraw.Draw(image)
        font = self.font_date  
        color = (0, 0, 0)
        bbox = draw.textbbox((0, 0), formatted, font=font)
        text_width = bbox[2] - bbox[0]
        x = 55
        y = 21
        draw.text((x, y), formatted, font=font, fill=color)
        
    def create_current_datetime_frame(self):
        """Crée un frame avec l'heure et la date actuelles"""
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        now = datetime.now()
        formatted = now.strftime("%d %B %Y")  # Même format que dans draw_datetime_block
        
        draw = ImageDraw.Draw(img)
        font = self.font_date  
        color = (0, 0, 0)  # Même couleur orange
        bbox = draw.textbbox((0, 0), formatted, font=font)
        text_width = bbox[2] - bbox[0]
        x = 55  # Même position X
        y = 21   # Même position Y
        draw.text((x, y), formatted, font=font, fill=color)
        
        return img

    def create_baisses_indices_table(self):
        """Crée le tableau des indices en baisse avec style bleu ciel et gris foncé"""
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Charger les données
        try:
            df = pd.read_csv('data_scrapped_csv/baisses_indices.csv')
            df = df.head(5)
            df = df[['Libellé', 'Cours', 'Var.(%)']]
            # print(f"📊 {len(df)} lignes de données des baisses d'indices chargées")
        except Exception as e:
            print(f"⚠️ Erreur chargement baisses indices: {e}")
            return img

        # Titre
        title = "Indices en Baisse"
        title_font = ImageFont.truetype(self.settings['font_bold'], self.settings['MASI_size'])
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = 75 + (300 - title_width) // 2
        title_y = 100
        draw.text((title_x, title_y), title, font=title_font, fill=(0, 0, 0))
        
        # 👉 Ajouter une image à gauche du titre
        try:
            icon = Image.open(self.settings['fleche_rouge_path']).convert("RGBA")

            # Redimensionner l'image à une hauteur cohérente avec le titre
            target_height = title_bbox[3] - title_bbox[1]
            scale = target_height / icon.height
            icon = icon.resize((int(icon.width * scale), target_height))

            icon_x = title_x - icon.width - 3  # 10px d'espacement
            icon_y = title_y + 5
            img.paste(icon, (icon_x, icon_y), mask=icon)
        except Exception as e:
            print(f"⚠️ Erreur chargement image d'icône : {e}")

        # Paramètres du tableau
        start_x = 40
        start_y = 130
        row_height = 25
        col_widths = [190, 100, 100]
        header_color = (173, 216, 230)
        row_colors = [(220, 220, 220), (240, 240, 240)]
        text_color = (0, 0, 0)
        border_color = (200, 200, 200)

        # En-têtes
        headers = ["Libellé", "Cours (MAD)", "Variation (%)"]
        for i, header in enumerate(headers):
            x = start_x + sum(col_widths[:i])
            draw.rectangle([x, start_y, x + col_widths[i], start_y + row_height], fill=header_color)
            draw.rectangle([x, start_y, x + col_widths[i], start_y + row_height], outline=border_color)
            bbox = draw.textbbox((x, start_y), header, font=self.font_table_bold)
            text_x = x + (col_widths[i] - (bbox[2] - bbox[0])) // 2
            text_y = start_y + (row_height - (bbox[3] - bbox[1])) // 2
            draw.text((text_x, text_y), header, font=self.font_table_bold, fill=(0, 0, 0))

        # Données
        for row_idx, row_data in enumerate(df.values.tolist()):
            y = start_y + (row_idx + 1) * row_height
            row_color = row_colors[row_idx % 2]
            for col_idx, cell in enumerate(row_data):
                x = start_x + sum(col_widths[:col_idx])
                draw.rectangle([x, y, x + col_widths[col_idx], y + row_height], fill=row_color)
                draw.rectangle([x, y, x + col_widths[col_idx], y + row_height], outline=border_color)
                
                cell_text = str(cell)
                # Choix de la police
                if col_idx == 0 and len(cell_text) > 18:
                    # Réduire la taille de la police pour libellé long
                    font = self.font_libelle_palmares
                else:
                    font = self.font_metal_bold

                bbox = draw.textbbox((x, y), cell_text, font=font)
                text_x = x + (col_widths[col_idx] - (bbox[2] - bbox[0])) // 2
                text_y = y + (row_height - (bbox[3] - bbox[1])) // 2
                draw.text((text_x, text_y), cell_text, font=font, fill=text_color)

        draw.rectangle([start_x, start_y, start_x + sum(col_widths), start_y + (len(df) + 1) * row_height], outline=(150, 150, 150), width=2)
        return img

    def create_hausses_indices_table(self):
        """Crée le tableau des indices en hausse avec style bleu ciel et gris foncé"""
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        try:
            df = pd.read_csv('data_scrapped_csv/hausse_indices.csv')
            df = df.head(5)
            df = df[['Libellé', 'Cours', 'Var.(%)']]
            # print(f"📊 {len(df)} lignes de données des hausses d'indices chargées")
        except Exception as e:
            print(f"⚠️ Erreur chargement hausses indices: {e}")
            return img

        title = "Indices en Hausse"
        title_font = ImageFont.truetype(self.settings['font_bold'], self.settings['MASI_size'])
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = 75 + (300 - title_width) // 2
        title_y = 320
        draw.text((title_x, title_y), title, font=title_font, fill=(0, 0, 0))
        
        # 👉 Ajouter une image à gauche du titre
        try:
            icon = Image.open(self.settings['fleche_verte_path']).convert("RGBA")

            # Redimensionner l'image à une hauteur cohérente avec le titre
            target_height = title_bbox[3] - title_bbox[1]
            scale = target_height / icon.height
            icon = icon.resize((int(icon.width * scale), target_height))

            icon_x = title_x - icon.width - 3  # 10px d'espacement
            icon_y = title_y + 5
            img.paste(icon, (icon_x, icon_y), mask=icon)
        except Exception as e:
            print(f"⚠️ Erreur chargement image d'icône : {e}")

        start_x = 40
        start_y = 350
        row_height = 25
        col_widths = [210, 100, 100]
        header_color = (173, 216, 230)
        row_colors = [(220, 220, 220), (240, 240, 240)]
        text_color = (0, 0, 0)
        border_color = (200, 200, 200)

        headers = ["Libellé", "Cours (MAD)", "Variation (%)"]
        for i, header in enumerate(headers):
            x = start_x + sum(col_widths[:i])
            draw.rectangle([x, start_y, x + col_widths[i], start_y + row_height], fill=header_color)
            draw.rectangle([x, start_y, x + col_widths[i], start_y + row_height], outline=border_color)
            bbox = draw.textbbox((x, start_y), header, font=self.font_table_bold)
            text_width = bbox[2] - bbox[0]
            text_height = bbox[3] - bbox[1]
            text_x = x + (col_widths[i] - text_width) // 2
            text_y = start_y + (row_height - text_height) // 2
            draw.text((text_x, text_y), header, font=self.font_table_bold, fill=(0, 0, 0))

        for row_idx, row_data in enumerate(df.values.tolist()):
            y = start_y + (row_idx + 1) * row_height
            row_color = row_colors[row_idx % 2]
            for col_idx, cell in enumerate(row_data):
                x = start_x + sum(col_widths[:col_idx])
                draw.rectangle([x, y, x + col_widths[col_idx], y + row_height], fill=row_color)
                draw.rectangle([x, y, x + col_widths[col_idx], y + row_height], outline=border_color)
                
                cell_text = str(cell)
                if col_idx == 0 and len(cell_text) > 18:
                    font = self.font_libelle_palmares
                else:
                    font = self.font_metal_bold

                bbox = draw.textbbox((x, y), cell_text, font=font)
                text_x = x + (col_widths[col_idx] - (bbox[2] - bbox[0])) // 2
                text_y = y + (row_height - (bbox[3] - bbox[1])) // 2
                draw.text((text_x, text_y), cell_text, font=font, fill=text_color)

        table_width = sum(col_widths)
        table_height = (len(df) + 1) * row_height
        draw.rectangle([start_x, start_y, start_x + table_width, start_y + table_height], outline=(150, 150, 150), width=2)

        return img

    
    def create_metaux_table(self):
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Charger les données
        try:
            df = pd.read_csv('data_scrapped_csv/metaux_precieux.csv')
            # print(f"📊 {len(df)} lignes de données des métaux précieux chargées")
        except Exception as e:
            print(f"⚠️ Erreur chargement données: {e}")
            return img

        # Titre du tableau
        title = "Métaux Précieux"
        title_font = ImageFont.truetype(self.settings['font_bold'], self.settings['MASI_size'])
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_x = 430 + (300 - (title_bbox[2] - title_bbox[0])) // 2
        title_y = 130
        draw.text((title_x, title_y), title, font=title_font, fill=(0, 0, 0))

        # Configuration tableau
        start_x = 460
        start_y = 160
        row_height = 25
        col_widths = [120, 70, 70]  # Colonnes de taille fixe
        header_color = (173, 216, 230)
        row_colors = [ (220, 220, 220), (173, 216, 230), (240, 240, 240)]
        text_color = (0, 0, 0)
        border_color = (200, 200, 200)

        # Afficher en-têtes dynamiquement
        for i, col in enumerate(df.columns):
            x = start_x + sum(col_widths[:i])
            draw.rectangle([x, start_y, x + col_widths[i], start_y + row_height], fill=header_color)
            draw.rectangle([x, start_y, x + col_widths[i], start_y + row_height], outline=border_color)

            text = str(col)
            bbox = draw.textbbox((x, start_y), text, font=self.font_table_bold)
            text_x = x + (col_widths[i] - (bbox[2] - bbox[0])) // 2
            text_y = start_y + (row_height - (bbox[3] - bbox[1])) // 2
            draw.text((text_x, text_y), text, font=self.font_table_bold, fill=text_color)

        # Afficher les lignes de données
        for row_idx, row in df.iterrows():
            y = start_y + (row_idx + 1) * row_height
            row_color = row_colors[row_idx % 2]

            for col_idx, value in enumerate(row):
                x = start_x + sum(col_widths[:col_idx])
                draw.rectangle([x, y, x + col_widths[col_idx], y + row_height], fill=row_color)
                draw.rectangle([x, y, x + col_widths[col_idx], y + row_height], outline=border_color)

                cell_text = str(value)
                bbox = draw.textbbox((x, y), cell_text, font=self.font_table_bold)
                text_x = x + (col_widths[col_idx] - (bbox[2] - bbox[0])) // 2
                text_y = y + (row_height - (bbox[3] - bbox[1])) // 2
                draw.text((text_x, text_y), cell_text, font=self.font_table_bold, fill=text_color)

        # Bordure du tableau complet
        table_width = sum(col_widths)
        table_height = (len(df) + 1) * row_height
        draw.rectangle([start_x, start_y, start_x + table_width, start_y + table_height], outline=(150, 150, 150), width=2)

        return img

    def create_devise_table(self):
        img = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Charger les données
        try:
            df = pd.read_csv('data_scrapped_csv/devise.csv')
            # print(f"📊 {len(df)} lignes de données des devises chargées")
        except Exception as e:
            print(f"⚠️ Erreur chargement données: {e}")
            return img

        # Titre du tableau
        title = "Devises"
        title_font = ImageFont.truetype(self.settings['font_bold'], self.settings['MASI_size'])
        title_bbox = draw.textbbox((0, 0), title, font=title_font)
        title_x = 430 + (300 - (title_bbox[2] - title_bbox[0])) // 2
        title_y = 350
        draw.text((title_x, title_y), title, font=title_font, fill=(0, 0, 0))

        # Configuration tableau
        start_x = 475
        start_y = 380
        row_height = 25
        col_widths = [90, 70, 70]  # Colonnes de taille fixe
        header_color = (220, 220, 220)
        row_colors = [ (173, 216, 230), (240, 240, 240)]
        text_color = (0, 0, 0)
        border_color = (200, 200, 200)

        # Afficher en-têtes dynamiquement
        for i, col in enumerate(df.columns):
            x = start_x + sum(col_widths[:i])
            draw.rectangle([x, start_y, x + col_widths[i], start_y + row_height], fill=header_color)
            draw.rectangle([x, start_y, x + col_widths[i], start_y + row_height], outline=border_color)

            text = str(col)
            bbox = draw.textbbox((x, start_y), text, font=self.font_table_bold)
            text_x = x + (col_widths[i] - (bbox[2] - bbox[0])) // 2
            text_y = start_y + (row_height - (bbox[3] - bbox[1])) // 2
            draw.text((text_x, text_y), text, font=self.font_table_bold, fill=text_color)

        # Afficher les lignes de données
        for row_idx, row in df.iterrows():
            y = start_y + (row_idx + 1) * row_height
            row_color = row_colors[row_idx % 2]

            for col_idx, value in enumerate(row):
                x = start_x + sum(col_widths[:col_idx])
                draw.rectangle([x, y, x + col_widths[col_idx], y + row_height], fill=row_color)
                draw.rectangle([x, y, x + col_widths[col_idx], y + row_height], outline=border_color)

                cell_text = str(value)
                bbox = draw.textbbox((x, y), cell_text, font=self.font_table)
                text_x = x + (col_widths[col_idx] - (bbox[2] - bbox[0])) // 2
                text_y = y + (row_height - (bbox[3] - bbox[1])) // 2
                draw.text((text_x, text_y), cell_text, font=self.font_table_bold, fill=text_color)

        # Bordure du tableau complet
        table_width = sum(col_widths)
        table_height = (len(df) + 1) * row_height
        draw.rectangle([start_x, start_y, start_x + table_width, start_y + table_height], outline=(150, 150, 150), width=2)

        return img
    
    def create_time_series_chart(self, progress=0.7):
        """Crée un graphique time series animé de gauche à droite avec curseur de progression"""
        try:
            # 1. Charger les données
            df_t = pd.read_csv('data_scrapped_csv/IntraDayDatas.csv', 
                            parse_dates=['Heure'], 
                            delimiter=';')
            df = df_t.iloc[::-1].reset_index(drop=True)
            
            # 2. Créer le graphique
            fig, ax = plt.subplots(figsize=(5, 4), dpi=80)
            
            # Titre du graphique
            fig.suptitle("Performance d'Indice MASI", y=1.02, fontsize=16, fontweight='bold')
            
            # Tracer la courbe complète en fond
            ax.plot(df['Heure'], df['Valeur'], color='#DDDDDD', linewidth=0.5, zorder=1)
            
            # Déterminer le nombre de points visibles
            visible_points = int(len(df) * progress)
            
            if visible_points > 0:
                # Tracer la partie visible
                ax.plot(df['Heure'][:visible_points], df['Valeur'][:visible_points], 
                    color='Black', linewidth=0.8, zorder=2)
                
                # Ajouter le curseur
                last_point = df.iloc[visible_points-1]
                ax.axvline(x=last_point['Heure'], color='red', linestyle='--', 
                        linewidth=0.5, alpha=0.6, zorder=3)
                
                # Ajouter le point rouge
                ax.scatter(last_point['Heure'], last_point['Valeur'], 
                        color='red', s=20, zorder=4)
                
                # Ajouter le texte
                ax.text(last_point['Heure'], last_point['Valeur'], 
                    f" {last_point['Valeur']:.2f}", 
                    color='red', fontsize=7, fontweight='bold',
                    verticalalignment='bottom', horizontalalignment='left',
                    bbox=dict(facecolor='white', alpha=0.7, edgecolor='none', pad=1.5),
                    zorder=5)
            
            # Configuration des axes
            if len(df) > 0:
                ax.set_xlim(df['Heure'].iloc[0], df['Heure'].iloc[-1])
                y_min = df['Valeur'].min() * 0.998
                y_max = df['Valeur'].max() * 1.002
                ax.set_ylim(y_min, y_max)
            
            # Style du graphique
            ax.grid(True, linestyle=':', alpha=0.3)
            ax.tick_params(axis='both', which='major', labelsize=7)
            ax.tick_params(axis='both', which='minor', labelsize=5)
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(maxticks=8))
            ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
            
            # Supprimer les bordures
            for spine in ax.spines.values():
                spine.set_visible(False)
            
            # Méthode robuste pour sauvegarder et charger l'image
            try:
                # Solution 1: Utilisation de BytesIO (mémoire)
                from io import BytesIO
                img_buffer = BytesIO()
                fig.savefig(img_buffer, format='png', 
                        transparent=True, 
                        bbox_inches='tight', 
                        pad_inches=0.05, 
                        dpi=80)
                img_buffer.seek(0)
                chart_img = Image.open(img_buffer).convert("RGBA")
                
                # Solution alternative 2: Fichier temporaire avec nom unique
                """
                import tempfile
                with tempfile.NamedTemporaryFile(suffix='.png', delete=True) as tmp:
                    fig.savefig(tmp.name, format='png', transparent=True, dpi=80)
                    chart_img = Image.open(tmp.name).convert("RGBA")
                """
                
                return chart_img
                
            except Exception as save_error:
                print(f"Erreur sauvegarde image: {save_error}")
                # Fallback: capture d'écran de la figure
                fig.canvas.draw()
                chart_img = Image.frombytes('RGB', 
                                        fig.canvas.get_width_height(),
                                        fig.canvas.tostring_rgb()).convert("RGBA")
                return chart_img
                
            finally:
                plt.close(fig)  # Fermer la figure dans tous les cas

        except Exception as e:
            print(f"⚠️ Erreur création graphique: {str(e)}")
            traceback.print_exc()
            # Retourner une image vide avec message d'erreur
            img = Image.new("RGBA", (450, 300), (0, 0, 0, 0))
            draw = ImageDraw.Draw(img)
            draw.text((10, 10), f"Erreur: {str(e)}", fill="red")
            return img

    def generate_video(self):
        df_news = pd.read_csv(self.settings['csv_path'])
        df_news = df_news.dropna(subset=['Intro'])
        print(f"📄 {len(df_news)} actualités chargées")
        out = cv2.VideoWriter('temp_video.mp4', cv2.VideoWriter_fourcc(*'mp4v'), 
                            self.settings['fps'], self.settings['resolution'])
        total_frame_count = 0
        current_news_index = 0
        max_ticker_frames = len(self.ticker_segments) * self.settings['fps'] * 4 #5
        
        # Ajout de la slide d'introduction avec animation du graphique
        if True:
            # Paramètres de l'animation
            chart_animation_duration = 6  # Durée totale de l'animation en secondes
            chart_animation_frames = chart_animation_duration * self.settings['fps']
            slide_duration_frames = self.settings['slide_duration'] * self.settings['fps']
            total_intro_frames = chart_animation_frames + slide_duration_frames
            
            for frame_idx in range(total_intro_frames):
                # Calculer la progression de l'animation (0 à 1)
                if frame_idx < chart_animation_frames:
                    progress = min(1.0, frame_idx / chart_animation_frames)
                else:
                    progress = 1.0  # Animation terminée
                
                # Préparer les composants
                background = self.gif_frames[self.current_gif_frame % len(self.gif_frames)]
                self.current_gif_frame += 1
                
                kpi_table = self.create_baisses_indices_table()
                sessions_table = self.create_hausses_indices_table() 
                meatux_table = self.create_metaux_table() 
                devises_table = self.create_devise_table()  
                chart_frame = self.create_time_series_chart(progress)
                datetime_frame = self.create_current_datetime_frame()
                self.total_frame_count = total_frame_count
                ticker_frame = self.create_ticker_frame(total_frame_count)
                market_table_frame = self.create_market_table_frame()
                
                # Position du graphique
                paste_x = 700 + (self.settings['image_max_width'] - chart_frame.width) // 2
                paste_y = 110 + (self.settings['image_max_height'] - chart_frame.height) // 2
                
                # Composition de l'image
                composed = Image.alpha_composite(background.copy(), kpi_table)
                composed = Image.alpha_composite(composed, sessions_table)
                composed = Image.alpha_composite(composed, meatux_table)
                composed = Image.alpha_composite(composed, devises_table)
                composed.paste(chart_frame, (paste_x, paste_y), chart_frame)
                composed = Image.alpha_composite(composed, datetime_frame)
                composed = Image.alpha_composite(composed, market_table_frame)
                composed = Image.alpha_composite(composed, ticker_frame)
                
                # Convertir et écrire la frame
                frame_bgr = cv2.cvtColor(np.array(composed.convert("RGB")), cv2.COLOR_RGB2BGR)
                out.write(frame_bgr)
                total_frame_count += 1
                
                if total_frame_count >= max_ticker_frames:
                    break
        
        while total_frame_count < max_ticker_frames:
            row = df_news.iloc[current_news_index % len(df_news)]
            title = str(row['Titre']) if pd.notna(row['Titre']) else ''
            intro = str(row['Intro']) if pd.notna(row['Intro']) else ''
            date_str = str(row['Date & Heure']) if 'Date & Heure' in row and pd.notna(row['Date & Heure']) else ''
            # img_path = os.path.join(self.settings['image_folder'], os.path.basename(str(row['URL Image']).split('?')[0])) if pd.notna(row['URL Image']) else None
            # Par cette version plus robuste :
            if pd.notna(row['URL Image']):
                url = str(row['URL Image'])
                # Nettoyer l'URL et extraire le nom de fichier
                filename = os.path.basename(url.split('?')[0].split('/')[-1])
                img_path = os.path.join(self.settings['image_folder'], filename)
                # Vérifier si le fichier existe
                if not os.path.exists(img_path):
                    print(f"⚠️ Fichier image introuvable: {img_path}")
                    img_path = None
            else:
                img_path = None
                
            background = self.gif_frames[self.current_gif_frame % len(self.gif_frames)]
            self.current_gif_frame += 1
            
            title_frame, title_final_y = self.create_title_frame(title)
            intro_frame = self.create_intro_frame(intro, title_final_y)
            image_frame = self.create_image_frame(img_path)
            datetime_frame = Image.new("RGBA", self.settings['resolution'], (0, 0, 0, 0))
            if date_str:
                self.draw_datetime_block(datetime_frame, date_str)
                
            self.total_frame_count = total_frame_count
            market_table_frame = self.create_market_table_frame()
            
            for _ in range(self.settings['slide_duration'] * self.settings['fps']):
                ticker_frame = self.create_ticker_frame(total_frame_count)
                composed = Image.alpha_composite(background.copy(), title_frame)
                composed = Image.alpha_composite(composed, intro_frame)
                composed = Image.alpha_composite(composed, image_frame)
                composed = Image.alpha_composite(composed, datetime_frame)
                composed = Image.alpha_composite(composed, market_table_frame)
                composed = Image.alpha_composite(composed, ticker_frame)
                frame_bgr = cv2.cvtColor(np.array(composed.convert("RGB")), cv2.COLOR_RGB2BGR)
                out.write(frame_bgr)
                total_frame_count += 1
                background = self.gif_frames[self.current_gif_frame % len(self.gif_frames)]
                self.current_gif_frame += 1
                if total_frame_count >= max_ticker_frames:
                    break
            print(f"✅ Slide {current_news_index + 1} générée")
            current_news_index += 1
        
        out.release()
        if os.path.exists(self.settings['audio_path']):
            subprocess.run([
                "ffmpeg", "-y", "-i", "temp_video.mp4", "-i", self.settings['audio_path'],
                "-c:v", "copy", "-c:a", "aac", "-shortest", self.settings['output_video']
            ], check=True)
            
            # if os.path.exists('temp_video.mp4'):
            #     os.remove('temp_video.mp4')
        else:
            os.rename("temp_video.mp4", self.settings['output_video'])
            
        # Nouvelle commande FFmpeg
        output_fixed = self.settings['output_video'].replace('_fixed.mp4','.mp4')
        subprocess.run([
            "ffmpeg", "-i", self.settings['output_video'],
            "-vcodec", "libx264", "-acodec", "aac", "-strict", "-2",
            output_fixed
        ], check=True)
        print(f"🎉 Vidéo générée : {self.settings['output_video']}")

if __name__ == "__main__":
    generator = NewsTemplateGenerator()
    generator.generate_video()