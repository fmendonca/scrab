from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import os
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfMerger
from weasyprint import HTML
from datetime import datetime
import uuid
import json
import logging

# Suprime o warning de vazamento de semáforos do multiprocessing no macOS
#import multiprocessing.resource_tracker
#multiprocessing.resource_tracker._RESOURCE_TYPES.remove('semaphore')

from crawler import crawl_and_generate_pdfs

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

LOG_FILE = os.path.join(OUTPUT_DIR, 'logs', 'app.log')
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s %(message)s')

SWAGGER_URL = '/docs'
API_URL = '/static/openapi.json'
swaggerui_blueprint = get_swaggerui_blueprint(SWAGGER_URL, API_URL, config={'app_name': "Flask PDF Scraper"})
app.register_blueprint(swaggerui_blueprint, url_prefix=SWAGGER_URL)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process', methods=['POST'])
def process_files_and_links():
    uploaded_pdfs = request.files.getlist("pdfs")
    urls = request.form.getlist("urls")
    pdf_paths = []

    for pdf_file in uploaded_pdfs:
        filename = f"{uuid.uuid4()}.pdf"
        path = os.path.join(UPLOAD_DIR, filename)
        pdf_file.save(path)
        pdf_paths.append(path)

    for url in urls:
        try:
            pdfs_from_url = crawl_and_generate_pdfs(url, OUTPUT_DIR, max_depth=2)
            pdf_paths.extend(pdfs_from_url)
        except Exception as e:
            logging.error(f"Erro processando {url}: {str(e)}")

    final_pdf_path = os.path.join(OUTPUT_DIR, f"merged_{uuid.uuid4()}.pdf")
    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(pdf)
    merger.write(final_pdf_path)
    merger.close()

    scraped_data = {}
    for url in urls:
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            title = soup.title.string if soup.title else "No title"
            paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
            scraped_data[url] = {
                "title": title,
                "paragraphs": paragraphs[:10]
            }
        except Exception as e:
            scraped_data[url] = {"error": str(e)}

    json_output_path = os.path.join(OUTPUT_DIR, f"scraped_{uuid.uuid4()}.json")
    with open(json_output_path, "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, ensure_ascii=False, indent=2)

    logging.info(f"PDFs: {[f.filename for f in uploaded_pdfs]}")
    logging.info(f"URLs: {urls}")
    logging.info(f"PDF final: {final_pdf_path}")
    logging.info(f"JSON scraping: {json_output_path}")

    history_path = os.path.join(OUTPUT_DIR, 'history.json')
    try:
        with open(history_path, 'r', encoding='utf-8') as hf:
            history = json.load(hf)
    except:
        history = []

    history.append({
        "timestamp": datetime.now().isoformat(),
        "pdfs_uploaded": [f.filename for f in uploaded_pdfs],
        "urls": urls,
        "pdf_result": final_pdf_path,
        "json_result": json_output_path
    })

    with open(history_path, 'w', encoding='utf-8') as hf:
        json.dump(history, hf, ensure_ascii=False, indent=2)

    return jsonify({
        "pdf_result": f"/output/{os.path.basename(final_pdf_path)}",
        "json_result": f"/output/{os.path.basename(json_output_path)}"
    })

@app.route('/output/<path:filename>')
def download_output(filename):
    return send_from_directory(OUTPUT_DIR, filename, as_attachment=False)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5555)
