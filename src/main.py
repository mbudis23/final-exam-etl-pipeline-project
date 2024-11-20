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

    # Load data Twitter
    try:
        logging.info("Loading Twitter data...")
        twitter_data = scrape_twitter("pendidikan indonesia")
        twitter_data.drop_duplicates(inplace=True)
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
        search_term = "pendidikan indonesia"
        days_back = 1
        posts = scrape_threads_search(
            search_term=search_term,
            max_posts=1000,
            days_back=days_back
        )
        thread_data = save_to_csv(posts, search_term)
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
        logging.info("Data combined successfully.")
    except Exception as e:
        logging.error(f"Error combining data: {e}")
        exit()

    # Proses sentimen
    try:
        logging.info("Starting sentiment labelling...")
        labelled_data = label_sentiment(combined_data, model_path)
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
        logging.info("Data cleaning completed successfully.")
    except Exception as e:
        logging.error(f"Error during data cleaning: {e}")
        exit()

    # Insert data into PostgreSQL
    try:
        logging.info("Inserting data into PostgreSQL...")
        conn = connect_db()
        for _, row in labelled_data.iterrows():
            try:
                insert_data(conn, {
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
