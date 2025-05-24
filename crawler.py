from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup
from weasyprint import HTML
import os
import uuid

def crawl_and_generate_pdfs(start_url, output_dir, max_depth=2):
    visited = set()
    to_visit = [(start_url, 0)]
    pdf_paths = []
    domain = urlparse(start_url).netloc

    while to_visit:
        current_url, depth = to_visit.pop(0)
        if current_url in visited or depth > max_depth:
            continue
        visited.add(current_url)

        try:
            print(f"Crawling: {current_url}")
            response = requests.get(current_url, timeout=10)
            response.raise_for_status()
            html_content = response.text

            # Salvar HTML e gerar PDF
            html_filename = f"{uuid.uuid4()}.html"
            html_path = os.path.join(output_dir, html_filename)
            with open(html_path, "w", encoding="utf-8") as f:
                f.write(html_content)

            pdf_filename = html_filename.replace(".html", ".pdf")
            pdf_output_path = os.path.join(output_dir, pdf_filename)
            HTML(string=html_content, base_url=current_url).write_pdf(pdf_output_path)
            pdf_paths.append(pdf_output_path)

            # Rastrear links internos
            if depth < max_depth:
                soup = BeautifulSoup(html_content, "html.parser")
                for link_tag in soup.find_all("a", href=True):
                    href = link_tag['href']
                    full_url = urljoin(current_url, href)
                    if urlparse(full_url).netloc == domain and full_url not in visited:
                        to_visit.append((full_url, depth + 1))
        except Exception as e:
            print(f"Erro ao processar {current_url}: {e}")

    return pdf_paths

