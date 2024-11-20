import os
import pandas as pd
# from utils.twitter_data_loader import load_twitter_data
from utils.scrapping_twitter import scrape_twitter
from utils.sentiment_labeller import label_sentiment
from datetime import datetime, timedelta
from utils.scrapping_threads import save_to_csv, scrape_threads_search
from utils.normalize import convert_column_to_integer, convert_column_to_string
from db.db_operations import connect_db, insert_data, close_connection

if __name__ == "__main__":
    # Path ke file CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # Path ke model
    model_path = os.path.join(current_dir, "../models/indobert_2024-11-19_14-31-19")

    # Load data Twitter
    try:
        print("Loading Twitter data...")
        twitter_data = scrape_twitter("pendidikan indonesia")
        print("Data loaded successfully!")
    except Exception as e:
        print(f"Error loading data: {e}")
        exit()

    # Load data Thread
    try:
        search_term = "pendidikan indonesia"
        days_back = 1
        now = datetime.now()
        cutoff_time = now - timedelta(days=days_back)
        
        posts = scrape_threads_search(
            search_term=search_term,
            max_posts=1000,
            days_back=days_back
        )
        
        
        print("Loading Thread data...")
        thread_data = save_to_csv(posts, search_term)
        print("Data loaded successfully!")
    except Exception as e:
        print(f"Error loading data: {e}")
        exit()

    # Combine Thread data
    try:
        thread_data['Views'] = None
        thread_data["Status ID"] = None
        twitter_data["Scraped At"] = datetime.now()
        combined_data = pd.concat([twitter_data, thread_data], ignore_index=True)
    except Exception as e:
        print(f"Error loading data: {e}")
        exit()

    # Proses sentimen
    try:
        print("Labelling sentiment...")
        labelled_data = label_sentiment(combined_data, model_path)
        print("Sentiment labelling completed!")
    except Exception as e:
        print(f"Error labelling sentiment: {e}")
        exit()

    # Data Cleaning
    try:
        print("Cleaning data...")
        labelled_data = convert_column_to_integer(labelled_data, "Likes")
        labelled_data = convert_column_to_integer(labelled_data, "Views")
        labelled_data = convert_column_to_integer(labelled_data, 'Replies')
        labelled_data = convert_column_to_integer(labelled_data, 'Reposts')
        labelled_data = convert_column_to_string(labelled_data, 'Status ID')
        labelled_data['Date'] = pd.to_datetime(labelled_data['Date'], errors='coerce', utc=True)
        labelled_data.drop_duplicates(inplace=True)
        print("Cleaning completed!")
    except Exception as e:
        print(f"Error Cleaning sentiment: {e}")
        exit()
        
    # Insert data into PostgreSQL
    try:
        print("Inserting data into PostgreSQL...")
        conn = connect_db()
        for _, row in labelled_data.iterrows():
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
        print("Data insertion completed!")
    except Exception as e:
        print(f"Error inserting data: {e}")
        exit()
    finally:
        close_connection(conn)
        
    print("Program Finish")
    # output_path = os.path.join(current_dir, f"../data-output/labelled_{datetime.now().strftime("%Y-%m-%d")}.csv")
    # labelled_data.to_csv(output_path, index=False)
    # print(labelled_data.info())
