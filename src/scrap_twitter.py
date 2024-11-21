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

    # Load data Twitter
    try:
        logging.info("Loading Twitter data...")
        twitter_data = scrape_twitter("pendidikan indonesia")
        twitter_data.drop_duplicates(inplace=True)
        twitter_data.to_csv('../twitter_data.csv', index=False)
        logging.info("Twitter data loaded successfully.")
        print('===================================================================================================')
        # print(twitter_data.isna().sum())
        print('===================================================================================================')
    except Exception as e:
        logging.error(f"Error loading Twitter data: {e}")
        exit()