# Flask PDF Scraper

Este projeto Flask permite:

1. Upload de um ou mais arquivos PDF.
2. Informar um ou mais links para baixar o conteúdo HTML e gerar PDF.
3. Fazer scraping do conteúdo e gerar um arquivo JSON com título e parágrafos.

## Instalação

```bash
pip install -r requirements.txt
```

É necessário ter o `wkhtmltopdf` instalado:
https://wkhtmltopdf.org/downloads.html

## Execução

```bash
python app.py
```

## Requisição

Você pode usar `curl`:

```bash
curl -X POST http://localhost:5000/process \
  -F "pdfs=@file1.pdf" \
  -F "pdfs=@file2.pdf" \
  -F "urls=https://example.com" \
  -F "urls=https://flask.palletsprojects.com"
```

## Saídas

- `output/merged_<uuid>.pdf` — PDF final combinado
- `output/scraped_<uuid>.json` — Conteúdo raspado dos sites
