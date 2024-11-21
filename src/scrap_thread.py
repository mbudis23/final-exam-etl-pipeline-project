import os
import pandas as pd
import logging
from utils.scrapping_twitter import scrape_twitter
from utils.sentiment_labeller import label_sentiment
from datetime import datetime, timedelta
from utils.scrapping_threads import save_to_csv, scrape_threads_search
from utils.normalize import convert_column_to_integer, convert_column_to_string
from db.db_operations import connect_db, insert_data, close_connection

logging.basicConfig(
    filename='data_pipeline.log',
    filemode='a',
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

if __name__ == "__main__":
    logging.info("Starting data pipeline process.")
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Path ke model
    model_path = os.path.join(current_dir, "../models/indobert_2024-11-19_14-31-19")

    # Load data Thread
    try:
        logging.info("Loading Threads data...")
        search_term = "pendidikan indonesia"
        days_back = 1
        posts = scrape_threads_search(
            search_term=search_term,
            max_posts=1000,
            days_back=days_back
        )
        thread_data = save_to_csv(posts, search_term)
        thread_data.to_csv('../thread_data.csv', index=False)
        logging.info("Threads data loaded successfully.")
        print('===================================================================================================')
        # print(thread_data.isna().sum())
        print('===================================================================================================')
    except Exception as e:
        logging.error(f"Error loading Threads data: {e}")
        exit()
