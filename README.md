# Telefinance 📊📹  
**End-to-end pipeline for generating streaming finance data and automated video content**

## 🚀 Overview
**Telefinance** is an end-to-end data pipeline designed to **scrape financial and news data**, **process and visualize it**, and **automatically generate short videos** combining charts, tables, and visual assets.  
The project is suitable for **financial media**, **Telegram/YouTube automation**, and **real-time market reporting** use cases.

## 🧩 Project Architecture
The pipeline follows these main steps:

1. **Data Scraping**
   - Scrapes financial market data and news from external sources
   - Stores structured outputs in CSV format

2. **Data Processing & Visualization**
   - Cleans and transforms data
   - Generates charts and tabular visuals

3. **Video Generation**
   - Combines charts, images, and templates
   - Produces automated finance videos (MP4)

## 📁 Project Structure
```
Telefinance/
│
├── data_scrapped_csv/      # Scraped financial & news data (CSV)
├── images_actualite/       # News-related images
├── scrapping_scripts/      # Web scraping scripts
├── static/                 # Static assets (CSS, images, JS)
├── templates/              # HTML templates for rendering visuals
├── video_components/       # Video building blocks
│
├── app1.py                 # Main application entry point
├── video_generation2.py    # Video generation logic
├── requirements.txt        # Python dependencies
├── temp_chart.png          # Sample generated chart
├── temp_video.mp4          # Sample generated video
```

## ⚙️ Technologies Used
- **Python**
- **BeautifulSoup / Requests** (scraping)
- **Pandas / NumPy** (data processing)
- **Matplotlib / Plotting tools** (charts)
- **MoviePy / FFmpeg** (video generation)
- **HTML / CSS** (templates)

## 🛠️ Installation
```bash
git clone https://github.com/hamzaih2k-1108/Telefinance.git
cd Telefinance
pip install -r requirements.txt
```

## ▶️ Usage
1. **Run data scraping**
```bash
python scrapping_scripts/<script_name>.py
```

2. **Generate visualizations & videos**
```bash
python video_generation2.py
```

3. **Launch main app**
```bash
python app1.py
```

## 📌 Example Output
- 📈 Auto-generated financial charts  
- 🧾 Scrolling market tables  
- 🎥 Automated finance news videos  

Sample files:
- `temp_chart.png`
- `temp_video.mp4`

## 🎯 Use Cases
- Financial news automation
- Stock market summaries
- Telegram / YouTube finance channels
- Data-driven media content generation

## 🧠 Future Improvements
- Real-time streaming integration (Kafka / WebSockets)
- Cloud deployment (AWS / GCP)
- Multi-language voice-over
- Stock market APIs integration
- Scheduling & orchestration (Airflow)

## 👤 Author
**Hamza Ihikki**  
Data Engineer | Data Scientist  
📍 Morocco  
🔗 GitHub: [hamzaih2k-1108](https://github.com/hamzaih2k-1108)

---

## ⭐ Support
If you find this project useful, consider **starring the repository** ⭐
