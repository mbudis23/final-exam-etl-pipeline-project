FROM apache/airflow:2.7.2

# Tambahkan dependensi tambahan jika diperlukan
RUN pip install --no-cache-dir pandas selenium bs4 torch transformers tqdm python-dotenv jmespath parsel nested-lookup playwright psycopg2-binary

# Set direktori kerja
WORKDIR /home/budi-setiawan/Repository/data-engineering/

# Salin DAG dan plugin tambahan (opsional)
COPY ./dags /home/budi-setiawan/Repository/data-engineering/dags
COPY ./plugins /home/budi-setiawan/Repository/data-engineering/plugins
