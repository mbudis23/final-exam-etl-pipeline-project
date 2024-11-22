import os
import pandas as pd
import logging
from utils.scrapping_twitter import scrape_twitter
from utils.sentiment_labeller import label_sentiment
from datetime import datetime, timedelta
from utils.scrapping_threads import save_to_csv, scrape_threads_search
from utils.normalize import convert_column_to_integer, convert_column_to_string
from db.db_operations import connect_db, insert_data, close_connection

# Configure logging
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
    twitter_data_path = os.path.join(current_dir, "../twitter_data.csv")
    thread_data_path = os.path.join(current_dir, "../thread_data.csv")
    # Load data Twitter
    try:
        logging.info("Loading Twitter data...")
        twitter_data = pd.read_csv(twitter_data_path)
        logging.info("Twitter data loaded successfully.")
        print('===================================================================================================')
        # print(twitter_data.isna().sum())
        print('===================================================================================================')
    except Exception as e:
        logging.error(f"Error loading Twitter data: {e}")
        exit()

    # Load data Thread
    try:
        logging.info("Loading Threads data...")
        thread_data = pd.read_csv(thread_data_path)
        logging.info("Threads data loaded successfully.")
        print('===================================================================================================')
        # print(thread_data.isna().sum())
        print('===================================================================================================')
    except Exception as e:
        logging.error(f"Error loading Threads data: {e}")
        exit()

    # Combine Thread data
    try:
        logging.info("Combining Twitter and Threads data...")
        thread_data['Views'] = None
        thread_data["Status ID"] = None
        twitter_data["Scraped At"] = datetime.now()
        combined_data = pd.concat([twitter_data, thread_data], ignore_index=True)
        combined_data.to_csv(os.path.join(current_dir, "../combined_data.csv"), index=False)
        logging.info("Data combined successfully.")
    except Exception as e:
        logging.error(f"Error combining data: {e}")
        exit()

    # Proses sentimen
    try:
        logging.info("Starting sentiment labelling...")
        labelled_data = label_sentiment(combined_data, model_path)
        labelled_data = combined_data
        # labelled_data['Sentiment'] = labelled_data['Likes'].apply(lambda x: 'Positive' if x > 100 else 'Negative')
        logging.info("Sentiment labelling completed successfully.")
        ('===================================================================================================')
        print(labelled_data.sample(5))
        print('===================================================================================================')
    except Exception as e:
        logging.error(f"Error during sentiment labelling: {e}")
        exit()

    # Data Cleaning
    try:
        logging.info("Starting data cleaning...")
        labelled_data = convert_column_to_integer(labelled_data, "Likes")
        labelled_data = convert_column_to_integer(labelled_data, "Views")
        labelled_data = convert_column_to_integer(labelled_data, 'Replies')
        labelled_data = convert_column_to_integer(labelled_data, 'Reposts')
        labelled_data = convert_column_to_string(labelled_data, 'Status ID')
        labelled_data['Date'] = pd.to_datetime(labelled_data['Date'], errors='coerce', utc=True)
        labelled_data.drop_duplicates(inplace=True)
        labelled_data['User'] = labelled_data['User'].str.replace(r'^@+', '', regex=True)
        labelled_data.to_csv(os.path.join(current_dir, "../cleaned_data.csv"), index=False)
        logging.info("Data cleaning completed successfully.")
    except Exception as e:
        logging.error(f"Error during data cleaning: {e}")
        exit()
