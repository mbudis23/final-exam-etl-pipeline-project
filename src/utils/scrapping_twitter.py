import os
import time
import logging
import urllib.parse
import re
from datetime import date, timedelta, datetime
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import pandas as pd

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def rename_columns(df, column_mapping):
    """
    Mengganti nama kolom pada DataFrame sesuai dengan mapping yang diberikan.

    Parameters:
    - df (pd.DataFrame): DataFrame yang kolomnya akan diubah.
    - column_mapping (dict): Dictionary mapping nama kolom lama ke nama kolom baru.

    Returns:
    - pd.DataFrame: DataFrame dengan kolom yang sudah diganti namanya.
    """
    logger.info("Renaming columns...")
    return df.rename(columns=column_mapping, inplace=False)

def scrape_twitter(search_term, max_tweets=1000, max_scrolls=10):
    logger.info("Initializing Selenium WebDriver...")
    driver = webdriver.Chrome()

    try:
        # Navigate to Twitter
        logger.info("Navigating to Twitter...")
        url = "https://x.com"
        driver.get(url)

        # Add authentication token
        token_value = os.getenv('TWITTER_AUTH_TOKEN')
        if token_value is None:
            logger.error("TWITTER_AUTH_TOKEN environment variable is not set. Please set it before running the script.")
            raise ValueError("TWITTER_AUTH_TOKEN is not set.")
        
        logger.info("Adding authentication cookie...")
        cookie = {
            "name": "auth_token",
            "value": token_value,
            "domain": ".x.com"
        }
        driver.add_cookie(cookie)
        driver.refresh()
        time.sleep(2)

        # Set up search dates and URL
        today = date.today().strftime("%Y-%m-%d")
        yesterday = (date.today() - timedelta(days=1)).strftime("%Y-%m-%d")
        encoded_search_term = urllib.parse.quote(search_term)
        search_url = f"https://x.com/search?q={encoded_search_term}%20since%3A{yesterday}%20until%3A{today}&src=typed_query"
        
        logger.info(f"Navigating to search URL: {search_url}")
        driver.get(search_url)
        time.sleep(5)

        # Initialize data collection
        data = []
        scroll_count = 0
        logger.info("Starting scraping process...")

        # Scraping loop
        while len(data) < max_tweets and scroll_count < max_scrolls:
            logger.info(f"Scroll attempt {scroll_count + 1}/{max_scrolls}. Collected {len(data)} tweets so far.")
            
            # Get page content
            soup = BeautifulSoup(driver.page_source, 'html.parser')

            # Parse tweets
            for div in soup.find_all("div", {"class": "css-175oi2r"}):
                tweets = div.find_all("article", {"data-testid": "tweet"})
                
                for tweet in tweets:
                    if len(data) >= max_tweets:
                        logger.info("Reached maximum number of tweets.")
                        break

                    try:
                        # Extract tweet data
                        tweet_text = tweet.find("div", {"data-testid": "tweetText"}).get_text() if tweet.find("div", {"data-testid": "tweetText"}) else None
                        username = (
                            tweet.find("div", {"data-testid": "User-Name"})
                            .find("span", string=lambda x: x and '@' in x).text
                            if tweet.find("div", {"data-testid": "User-Name"}) and tweet.find("div", {"data-testid": "User-Name"}).find("span", string=lambda x: x and '@' in x)
                            else ""
                        )
                        retweets = (
                            tweet.find("button", {"data-testid": "retweet"})
                            .find("span", {"class": "css-1jxf684"}).text
                            if tweet.find("button", {"data-testid": "retweet"})
                            else "0"
                        )
                        likes = (
                            tweet.find("button", {"data-testid": "like"})
                            .find("span", {"class": "css-1jxf684"}).text
                            if tweet.find("button", {"data-testid": "like"})
                            else "0"
                        )
                        views = (
                            tweet.find("a", {"aria-label": lambda x: x and 'views' in x})
                            .find("span", {"class": "css-1jxf684"}).text
                            if tweet.find("a", {"aria-label": lambda x: x and 'views' in x})
                            else "0"
                        )

                        # Extract post creation date
                        time_element = tweet.find("time")
                        created_at = None
                        if time_element and 'datetime' in time_element.attrs:
                            created_at = datetime.strptime(
                                time_element['datetime'], "%Y-%m-%dT%H:%M:%S.%fZ"
                            ).strftime("%Y-%m-%d %H:%M:%S")

                        # Extract status ID
                        status_links = tweet.find_all("a", href=re.compile(r"/status/\d+"))
                        status_id = None
                        for link in status_links:
                            match = re.search(r"/status/(\d+)", link['href'])
                            if match:
                                status_id = match.group(1)
                                break

                        # Store tweet data
                        data.append({
                            "Tweet Text": tweet_text,
                            "Username": username,
                            "Likes": likes,
                            "Retweets": retweets,
                            "Views": views,
                            "Status ID": status_id,
                            "Created At": created_at,
                        })
                    except Exception as e:
                        logger.error(f"Error parsing tweet: {str(e)}")
                        continue

            # Scroll down to load more tweets
            logger.info("Scrolling down...")
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            scroll_count += 1

        logger.info(f"Scraping completed. Collected {len(data)} tweets.")

        # Create DataFrame
        df = pd.DataFrame(data)

        # Rename columns
        column_mapping = {
            'Created At': 'Date', 
            'Username': 'User', 
            'Tweet Text': 'Text',
            'Retweets' : 'Reposts',
            'likes': 'Likes'
        }
        mapping_df = rename_columns(df, column_mapping)
        mapping_df['Platform'] = 'twitter'
        
        logger.info("Data processing complete. Returning DataFrame.")
        return mapping_df

    except Exception as e:
        logger.error(f"An error occurred during scraping: {str(e)}")
        driver.quit()
        raise

    finally:
        driver.quit()



# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service
# from selenium.webdriver.common.by import By
# from selenium.webdriver.common.keys import Keys
# from datetime import date, timedelta
# from datetime import datetime
# import time
# import urllib.parse
# import pandas as pd
# import datetime
# from bs4 import BeautifulSoup
# import re
# import os
# from dotenv import load_dotenv

# load_dotenv()

# def rename_columns(df, column_mapping):
#     """
#     Mengganti nama kolom pada DataFrame sesuai dengan mapping yang diberikan.

#     Parameters:
#     - df (pd.DataFrame): DataFrame yang kolomnya akan diubah.
#     - column_mapping (dict): Dictionary mapping nama kolom lama ke nama kolom baru.

#     Returns:
#     - pd.DataFrame: DataFrame dengan kolom yang sudah diganti namanya.
#     """
#     return df.rename(columns=column_mapping, inplace=False)

# def scrape_twitter(search_term, max_tweets=1000, max_scrolls=10):
#     # Initialize webdriver
#     driver = webdriver.Chrome()
#     url = "https://x.com"
#     driver.get(url)

#     # Add authentication token
#     token_value = os.getenv('TWITTER_AUTH_TOKEN')
#     if token_value is None:
#         raise ValueError("TWITTER_AUTH_TOKEN environment variable is not set. Please set it before running the script.")
    
#     cookie = {
#         "name": "auth_token",
#         "value": token_value,
#         "domain": ".x.com"
#     }
#     driver.add_cookie(cookie)
#     driver.refresh()
#     time.sleep(2)

#     # Set up search dates and URL
#     today = date.today()
#     yesterday = today - timedelta(days=1)
#     today = today.strftime("%Y-%m-%d")
#     yesterday = yesterday.strftime("%Y-%m-%d")
    
#     encoded_search_term = urllib.parse.quote(search_term)
#     search_url = f"https://x.com/search?q={encoded_search_term}%20since%3A{yesterday}%20until%3A{today}&src=typed_query"
    
#     driver.get(search_url)
#     time.sleep(5)

#     # Initialize data collection
#     data = []
#     scroll_count = 0

#     # Scraping loop
#     while len(data) < max_tweets and scroll_count < max_scrolls:
#         # Get page content
#         soup = BeautifulSoup(driver.page_source, 'html.parser')

#         # Parse tweets
#         for div in soup.find_all("div", {"class": "css-175oi2r"}):
#             heading = div.find("h1").get_text() if div.find("h1") else None
#             tweets = div.find_all("article", {"data-testid": "tweet"})
            
#             for tweet in tweets:
#                 if len(data) >= max_tweets:
#                     break

#                 # Extract tweet data
#                 tweet_text = tweet.find("div", {"data-testid": "tweetText"}).get_text() if tweet.find("div", {"data-testid": "tweetText"}) else None
#                 username = (
#                     tweet.find("div", {"data-testid": "User-Name"})
#                     .find("span", string=lambda x: x and '@' in x).text
#                     if tweet.find("div", {"data-testid": "User-Name"}) and tweet.find("div", {"data-testid": "User-Name"}).find("span", string=lambda x: x and '@' in x)
#                     else ""
#                 )
#                 retweets = (
#                     tweet.find("button", {"data-testid": "retweet"})
#                     .find("span", {"class": "css-1jxf684"}).text
#                     if tweet.find("button", {"data-testid": "retweet"})
#                     else "0"
#                 )
#                 likes = (
#                     tweet.find("button", {"data-testid": "like"})
#                     .find("span", {"class": "css-1jxf684"}).text
#                     if tweet.find("button", {"data-testid": "like"})
#                     else "0"
#                 )
#                 views = (
#                     tweet.find("a", {"aria-label": lambda x: x and 'views' in x})
#                     .find("span", {"class": "css-1jxf684"}).text
#                     if tweet.find("a", {"aria-label": lambda x: x and 'views' in x})
#                     else "0"
#                 )

#                 # Extract post creation date
#                 time_element = tweet.find("time")
#                 created_at = None
#                 if time_element and 'datetime' in time_element.attrs:
#                     created_at = datetime.datetime.strptime(
#                         time_element['datetime'], 
#                         "%Y-%m-%dT%H:%M:%S.%fZ"
#                     ).strftime("%Y-%m-%d %H:%M:%S")

#                 # Extract status ID
#                 status_links = tweet.find_all("a", href=re.compile(r"/status/\d+"))
#                 status_id = None
#                 for link in status_links:
#                     match = re.search(r"/status/(\d+)", link['href'])
#                     if match:
#                         status_id = match.group(1)
#                         break

#                 # Store tweet data
#                 data.append({
#                     "Tweet Text": tweet_text,
#                     "Username": username,
#                     "Likes": likes,
#                     "Retweets": retweets,
#                     "Views": views,
#                     "Status ID": status_id,
#                     "Created At": created_at,  # New column for post creation date
#                 })

#         # Scroll down to load more tweets
#         driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
#         time.sleep(2)
#         scroll_count += 1

#     # Close the browser
#     driver.quit()

#     # Create DataFrame
#     df = pd.DataFrame(data)

#     # Ubah nama kolom
#     column_mapping = {
#         'Datetime': 'Date', 
#         'Username': 'User', 
#         'Tweet Text': 'Tweet'
#     }
#     mapping_df = rename_columns(df, column_mapping)
#     mapping_df['Platform'] = 'twitter'
    
#     return mapping_df