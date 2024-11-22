# 🎓 **Analisis Sentimen Pendidikan Indonesia**

## 📝  Demo
- [Blog Post](https://habib-fabian.notion.site/ETL-Process-Data-Pipeline-untuk-Klasifikasi-Analisis-Sentimen-dari-Platform-Threads-X-14369c9453bf808a855fd495c3031512)
- [Video Demo](https://drive.google.com/drive/folders/1YRSE9O3M66stHPM1mk-Vo2JrZ3DvNu9z?usp=sharing)
---

## **Deskripsi**
Pendidikan merupakan pilar utama dalam membangun bangsa. Di Indonesia, dengan populasi lebih dari 270 juta jiwa dan lebih dari 300.000 sekolah, sistem pendidikan menghadapi tantangan besar dalam mengelola, menganalisis, dan memahami data. Selain itu, opini publik terhadap sistem pendidikan seringkali tersebar luas melalui media sosial. Dengan memahami opini ini, pengambil kebijakan dapat memperoleh wawasan untuk meningkatkan kualitas pendidikan nasional.

Proyek ini dirancang untuk mengimplementasikan pipeline ETL (Extract, Transform, Load) yang mengolah data dari dua platform media sosial, Threads dan X (sebelumnya dikenal sebagai Twitter). Pipeline ini tidak hanya mengekstrak data mentah, tetapi juga membersihkan, menganalisis, dan mengklasifikasikan sentimen publik menjadi kategori positif, netral, atau negatif. Seluruh data yang diproses akan disimpan di database PostgreSQL yang dikelola oleh Supabase dan divisualisasikan menggunakan Tableau untuk menghasilkan dashboard yang interaktif dan mudah dipahami.

Proses ETL ini bertujuan untuk membantu pemangku kepentingan dalam:

    1. Memantau opini publik terkait topik pendidikan.
    2. Menyediakan data akurat untuk mendukung keputusan berbasis data.
    3. Mengidentifikasi tren dan pola dalam diskusi publik tentang pendidikan.

Melalui pipeline ETL ini, proses pengolahan data sentimen dapat dilakukan secara otomatis, cepat, dan terstruktur. Data yang dihasilkan memungkinkan pemangku kepentingan untuk mendapatkan wawasan strategis tentang opini publik terhadap pendidikan nasional. Dengan dukungan teknologi seperti Apache Airflow, Supabase, dan Tableau, proyek ini menciptakan sistem analisis yang efisien, skalabel, dan berkelanjutan.



---

## **Fitur Utama**
- **Ekstraksi Data Otomatis**: Mengambil data dari Threads dan X secara terstruktur. Pengambilan menggunakan teknik scraping web.
- **Transformasi Data**: Membersihkan dan mengolah data untuk analisis sentimen menggunakan model machine learning.
- **Klasifikasi Sentimen**: Menentukan sentimen (positif, netral, negatif) dengan NLP dari afbudiman/indobert-classification.
- **Penyimpanan Data**: Menyimpan hasil analisis ke PostgreSQL yang dikelola oleh Supabase.
- **Visualisasi**: Data yang telah diolah divisualisasikan menggunakan Tableau. Diagram menyoroti visualisasi seperti tren sentimen, pemetaan topik, dan analisis berbasis kata kunci.
---

## **Teknologi yang Digunakan**
![Python](https://img.shields.io/badge/-Python-3776AB?logo=python&logoColor=white)
![Airflow](https://img.shields.io/badge/-Airflow-017CEE?logo=apache-airflow&logoColor=white)
![Supabase](https://img.shields.io/badge/-Supabase-3ECF8E?logo=supabase&logoColor=white)
![Tableau](https://img.shields.io/badge/-Tableau-E97627?logo=tableau&logoColor=white)

**Library Python**:
- `pandas`
- `selenium`
- `beautifulsoup4`
- `torch`
- `transformers`
- `tqdm`
- `python-dotenv`
- `jmespath`
- `parsel`
- `nested-lookup`
- `playwright`
- `psycopg2-binary`

---

## **Prasyarat**
1. **Software**:
   - Python 3.8+
   - PostgreSQL
   - Apache Airflow
2. **Environment Variables**:
   Pastikan Anda memiliki file `.env` dengan variabel berikut:
   ```env
   # Twitter API Authentication
   TWITTER_AUTH_TOKEN=your_twitter_auth_token

   # Instagram Authentication
   INSTAGRAM_USERNAME=your_instagram_username
   INSTAGRAM_PASSWORD=your_instagram_password

   # Database Configuration
   DATABASE_NAME=your_database_name
   USER=your_database_user
   PASSWORD=your_database_password
   HOST=your_database_host
   PORT=your_database_port
   ```

---

## **Instalasi**

### **1. Clone Repository**
```bash
git clone https://github.com/mbudis23/final-exam-etl-pipeline-project
cd final-exam-etl-pipeline-project
```

### **2. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **3. Konfigurasi Environment**
- Buat file `.env` di root proyek.
- Salin template variabel lingkungan dari bagian **Prasyarat** di atas.
- Masukkan nilai yang sesuai dengan konfigurasi Anda.

### **4. Install Apache Airflow**
- **Buat Virtual Environment** 
  ```bash
  python -m venv venv
  source venv/bin/activate  # Linux/Mac
  ```
- **Install Airflow**
  ```bash
  pip install apache-airflow
  ```
- **Inisialisasi Database Airflow**
  ```bash
  airflow db init
  ```
- **Buat User Admin**
  ```bash
  airflow users create \
      --username admin \
      --firstname Admin \
      --lastname User \
      --role Admin \
      --email admin@example.com
  ```
- **Jalankan Airflow**
  Gunakan dua terminal:
  - **Terminal 1**: Jalankan Webserver
    ```bash
    airflow webserver --port 8080
    ```
  - **Terminal 2**: Jalankan Scheduler
    ```bash
    airflow scheduler
    ```

### **5. Tambahkan DAG ke Airflow**
- Salin file DAG ke folder Airflow:
  ```bash
  cp dags/daily_main_py_dag.py $AIRFLOW_HOME/dags/
  ```

### **6. Jalankan Pipeline**
- Buka Airflow di browser di [http://localhost:8080](http://localhost:8080).
- Cari DAG `daily_main_py_dag` dan klik "Trigger DAG" untuk menjalankan pipeline.

---

## **Lisensi**
Proyek ini dilisensikan di bawah [MIT License](LICENSE).