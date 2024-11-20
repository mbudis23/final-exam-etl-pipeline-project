entimen
    # try:
    #     logging.info("Starting sentiment labelling...")
    #     labelled_data = label_sentiment(combined_data, model_path)
    #     logging.info("Sentiment labelling completed successfully.")
    # except Exception as e:
    #     logging.error(f"Error during sentiment labelling: {e}")
    #     exit()

    # # Data Cleaning
    # try:
    #     logging.info("Starting data cleaning...")
    #     labelled_data = convert_column_to_integer(labelled_data, "Likes")
    #     labelled_data = convert_column_to_integer(labelled_data, "Views")
    #     labelled_data = convert_column_to_integer(labelled_data, 'Replies')
    #     labelled_data = convert_column_to_integer(labelled_data, 'Reposts')
    #     labelled_data = convert_column_to_string(labelled_data, 'Status ID')
    #     labelled_data['Date'] = pd.to_datetime(labelled_data['Date'], errors='coerce', utc=True)
    #     labelled_data.drop_duplicates(inplace=True)
    #     logging.info("Data cleaning completed successfully.")
    # except Exception as e:
    #     logging.error(f"Error during data cleaning: {e}")
    #     exit()