import os
from utils.twitter_data_loader import load_twitter_data
from utils.sentiment_labeller import label_sentiment

if __name__ == "__main__":
    # Path ke file CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "../data-output/tweets_pendidikan indonesia_since-2024-11-12_until-2024-11-13.csv")

    # Load data
    try:
        df = load_twitter_data(file_path)
        print("Load twitter success")  # Menampilkan 5 baris pertama dari DataFrame
    except Exception as e:
        print(f"Error: {e}")

    # Label sentimen
    try:
        result_df = label_sentiment(df)
        print(result_df['User', 'sentiment'])
    except Exception as e:
        print(f"Error: {e}")
