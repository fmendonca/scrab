import requests

files = [
    ('pdfs', open('sample1.pdf', 'rb')),
    ('pdfs', open('sample2.pdf', 'rb')),
]

urls = [
    ('urls', 'https://example.com'),
    ('urls', 'https://www.python.org'),
]

response = requests.post('http://localhost:5000/process', files=files, data=urls)

if response.ok:
    data = response.json()
    print("PDF result:", data['pdf_result'])
    print("JSON result:", data['json_result'])
else:
    print("Erro ao processar:", response.text)
