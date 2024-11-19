import os
from utils.twitter_data_loader import load_twitter_data
from utils.sentiment_labeller import label_sentiment

if __name__ == "__main__":
    # Path ke file CSV
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "../data-output/tweets_pendidikan.csv")

    # Path ke model
    model_path = os.path.join(current_dir, "../models/indobert_2024-11-19_14-31-19")

    # Load data Twitter
    try:
        print("Loading Twitter data...")
        twitter_data = load_twitter_data(file_path)
        print("Data loaded successfully!")
    except Exception as e:
        print(f"Error loading data: {e}")
        exit()

    # Proses sentimen
    try:
        print("Labelling sentiment...")
        labelled_data = label_sentiment(twitter_data, model_path)
        print("Sentiment labelling completed!")
    except Exception as e:
        print(f"Error labelling sentiment: {e}")
        exit()

    # Simpan hasil ke file baru
    output_path = os.path.join(current_dir, "../data-output/tweets_pendidikan.csv")
    labelled_data.to_csv(output_path, index=False)
    print(f"Processed data saved to: {output_path}")
