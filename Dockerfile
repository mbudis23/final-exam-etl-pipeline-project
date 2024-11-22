# Gunakan base image Python
FROM python:3.9-slim

# Set working directory
WORKDIR /app

# Salin semua file proyek ke dalam container
COPY . .

# Install dependensi Python
RUN pip install --upgrade pip && pip install -r requirements.txt

# Install Playwright dan browser dependencies
RUN apt-get update && apt-get install -y libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libxkbcommon0 libdrm2 libgbm1 libasound2 libxcomposite1 libxrandr2 libgtk-3-0 libxshmfence1 \
    && playwright install

# Jalankan skrip utama (ubah sesuai kebutuhan)
CMD ["python", "src/main.py"]
