FROM python:3.11-slim

# Instala wkhtmltopdf e dependências
RUN apt-get update && apt-get install -y \
    wkhtmltopdf \
    libxrender1 \
    libxext6 \
    libfontconfig1 \
    && apt-get clean

# Diretório da aplicação
WORKDIR /app

# Copia os arquivos
COPY . /app

# Instala as dependências
RUN pip install --no-cache-dir -r requirements.txt

# Porta padrão do Flask
EXPOSE 5000

# Comando para iniciar o servidor
CMD ["python", "app.py"]
