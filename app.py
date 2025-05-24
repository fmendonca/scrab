from flask import Flask, request, jsonify
from flask_cors import CORS
import os
import requests
from bs4 import BeautifulSoup
import pdfkit
from PyPDF2 import PdfMerger
import uuid
import json

app = Flask(__name__)
CORS(app)

UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

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
            html_content = requests.get(url).text
            html_filename = f"{uuid.uuid4()}.html"
            html_path = os.path.join(OUTPUT_DIR, html_filename)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)
            pdf_filename = html_filename.replace(".html", ".pdf")
            pdf_output_path = os.path.join(OUTPUT_DIR, pdf_filename)
            pdfkit.from_file(html_path, pdf_output_path)
            pdf_paths.append(pdf_output_path)
        except Exception as e:
            print(f"Erro processando URL {url}: {e}")

    merger = PdfMerger()
    for pdf in pdf_paths:
        merger.append(pdf)

    final_pdf_path = os.path.join(OUTPUT_DIR, f"merged_{uuid.uuid4()}.pdf")
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

    return jsonify({
        "pdf_result": final_pdf_path,
        "json_result": json_output_path
    })

if __name__ == '__main__':
    app.run(debug=True)
