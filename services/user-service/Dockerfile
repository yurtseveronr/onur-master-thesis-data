# Base image olarak Python 3.10 kullan
FROM python:3.10

# Çalışma dizinini ayarla
WORKDIR /app

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Uygulama dosyalarını kopyala
COPY . .

# Uygulamayı 8080 portunda başlat
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080"]
