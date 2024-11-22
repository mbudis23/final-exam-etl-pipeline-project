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
    logging.info("Starting Load process.")
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Path ke model
    model_path = os.path.join(current_dir, "../models/indobert_2024-11-19_14-31-19")
    cleaning_data = os.path.join(current_dir, "../cleaned_data.csv")
    # Load data Twitter
    try:
        logging.info("Loading cleaned data...")
        twitter_data = pd.read_csv(cleaning_data, dtype={'Status ID': str})
        logging.info("Twitter data loaded successfully.")
        print('===================================================================================================')
        # print(twitter_data.isna().sum())
        print('===================================================================================================')
    except Exception as e:
        logging.error(f"Error loading Twitter data: {e}")
        exit()

    try:
        logging.info("Inserting data into PostgreSQL...")
        conn = connect_db()
        for _, row in twitter_data.iterrows():
            try:
                insert_data(conn, {
                    'Text': row['Text'],
                    'Text': row['Text'],
                    'User': row['User'],
                    'Likes': row['Likes'],
                    'Reposts': row['Reposts'],
                    'Date': row['Date'],
                    'Platform': row['Platform'],
                    'Scraped At': row['Scraped At'],
                    'Sentiment': row['Sentiment'],
                    'Views': row['Views'],
                    'Status ID': row['Status ID'],
                    'Replies': row['Replies']
                })
                logging.info(f"Data inserted successfully for User: {row['User']} on Platform: {row['Platform']}.")
            except Exception as inner_e:
                logging.error(f"Error inserting row for User: {row['User']} on Platform: {row['Platform']}: {inner_e}")
        logging.info("Data insertion completed successfully.")
    except Exception as e:
        logging.error(f"Error during data insertion: {e}")
        exit()
    finally:
        close_connection(conn)
        logging.info("Database connection closed.")

    logging.info("Program finished successfully.")
