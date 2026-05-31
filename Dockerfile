FROM python:3.12-slim

# Çalışma dizinini ayarla
WORKDIR /app

# İşletim sistemi bağımlılıklarını kur (psycopg2-binary vb. için gerekli olabilir)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Gereksinim dosyasını kopyala ve kütüphaneleri kur
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projenin kalanını kopyala
COPY . .

# Flask'ı production (gunicorn) üzerinden dışarıya aç
EXPOSE 5000

# Gunicorn ile uygulamayı başlat (4 worker)
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "run:app"]
