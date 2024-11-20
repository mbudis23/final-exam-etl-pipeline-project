import psycopg2

db_params = {
    'dbname': 'data_engineering',
    'user': 'postgres',
    'password': '12345678',
    'host': 'localhost'  # Update as needed
}

def connect_db():
    """Establish a connection to the database."""
    try:
        conn = psycopg2.connect(**db_params)
        print("Database connection established.")
        return conn
    except Exception as e:
        raise Exception(f"Error connecting to the database: {e}")

def insert_data(conn, row):
    """
    Inserts data into the main table and platform-specific tables based on the platform type.
    Checks for duplicate entries to prevent duplication.

    :param conn: Database connection
    :param row: Dictionary containing the data to insert
    """
    try:
        with conn.cursor() as cur:
            # Check if the data already exists in main_data
            cur.execute("""
                SELECT id FROM main_data
                WHERE text = %s AND user_handle = %s AND date = %s AND platform = %s
            """, (row['Text'], row['User'], row['Date'], row['Platform']))
            main_result = cur.fetchone()

            if main_result:
                main_id = main_result[0]
                print(f"Duplicate found in main_data for ID: {main_id}")
            else:
                # Insert into main_data
                cur.execute("""
                    INSERT INTO main_data (text, user_handle, likes, reposts, date, platform, scraped_at, sentiment)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s) RETURNING id
                """, (row['Text'], row['User'], row['Likes'], row['Reposts'], row['Date'], row['Platform'], row['Scraped At'], row['Sentiment']))
                main_id = cur.fetchone()[0]  # Get the ID of the inserted row
                print(f"Data inserted into main_data with ID: {main_id}")

            # Insert into platform-specific tables
            if row['Platform'].lower() == 'twitter':
                # Check for duplicates in twitter_data
                cur.execute("""
                    SELECT id FROM twitter_data
                    WHERE main_id = %s AND status_id = %s
                """, (main_id, row['Status ID']))
                twitter_result = cur.fetchone()

                if twitter_result:
                    print(f"Duplicate found in twitter_data for main_id: {main_id}")
                else:
                    cur.execute("""
                        INSERT INTO twitter_data (main_id, views, status_id)
                        VALUES (%s, %s, %s)
                    """, (main_id, row['Views'], row['Status ID']))
                    print(f"Data inserted into twitter_data for main_id: {main_id}")

            elif row['Platform'].lower() == 'threads':
                # Check for duplicates in thread_data
                cur.execute("""
                    SELECT id FROM thread_data
                    WHERE main_id = %s
                """, (main_id,))
                thread_result = cur.fetchone()

                if thread_result:
                    print(f"Duplicate found in thread_data for main_id: {main_id}")
                else:
                    cur.execute("""
                        INSERT INTO thread_data (main_id, replies)
                        VALUES (%s, %s)
                    """, (main_id, row['Replies']))
                    print(f"Data inserted into thread_data for main_id: {main_id}")

            conn.commit()
    except Exception as e:
        conn.rollback()
        raise Exception(f"Error inserting data: {e}")

def close_connection(conn):
    """Closes the database connection."""
    try:
        conn.close()
        print("Database connection closed.")
    except Exception as e:
        raise Exception(f"Error closing the connection: {e}")
