import json
from typing import Dict, List
import jmespath
from parsel import Selector
from nested_lookup import nested_lookup
from playwright.sync_api import sync_playwright, TimeoutError
import logging
from datetime import datetime, timedelta
import time
from urllib.parse import quote
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Set up logging
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

def click_login_button(page):
    """Click the initial login button/link on Threads"""
    try:
        logger.info("Looking for login button...")
        selectors = [
            'a[href*="/login/"][role="link"]',
            'div.x78zum5 a[href*="/login/"]',
            'a.x1i10hfl[href*="/login/"]',
            'a:has-text("Log in")'
        ]
        
        for selector in selectors:
            try:
                element = page.wait_for_selector(selector, timeout=5000)
                if element:
                    logger.info(f"Found login button with selector: {selector}")
                    element.click()
                    time.sleep(3)
                    return True
            except:
                continue
                
        return False
        
    except Exception as e:
        logger.error(f"Error clicking login button: {str(e)}")
        return False

def perform_threads_login(page):
    """Login to Threads"""
    try:
        logger.info("Starting Threads login process...")
        
        # Get credentials
        username = os.getenv('INSTAGRAM_USERNAME')
        password = os.getenv('INSTAGRAM_PASSWORD')
        
        if not username or not password:
            raise ValueError("Instagram credentials not found in .env file")

        # Wait for and fill username
        logger.info("Waiting for username field...")
        username_selector = 'input[name="username"],input[type="text"][placeholder="Username, phone or email"]'
        page.wait_for_selector(username_selector, timeout=10000)
        page.fill(username_selector, username)
        time.sleep(1)
        
        # Fill password
        logger.info("Filling password...")
        password_selector = 'input[name="password"],input[type="password"]'
        page.fill(password_selector, password)
        time.sleep(1)
        
        # Click login button
        logger.info("Clicking login button...")
        login_button_selectors = [
            'button[type="submit"]',
            'div[role="button"]:has-text("Log in")',
            'button:has-text("Log in")'
        ]
        
        for selector in login_button_selectors:
            try:
                button = page.wait_for_selector(selector, timeout=5000)
                if button:
                    button.click()
                    break
            except:
                continue
        
        # Wait for login completion
        logger.info("Waiting for login completion...")
        time.sleep(5)
        
        # Check for successful login
        success_selectors = [
            'input[placeholder="Search"]',
            'div[role="main"]',
            'div[data-pressable-container="true"]'
        ]
        
        for selector in success_selectors:
            try:
                page.wait_for_selector(selector, timeout=10000)
                logger.info("Login successful")
                return True
            except:
                continue
                
        logger.error("Login verification failed")
        return False
        
    except Exception as e:
        logger.error(f"Login failed: {str(e)}")
        return False

def wait_for_threads_content(page):
    """Wait for Threads content to load with improved selectors"""
    selectors = [
        'div[class*="x78zum5"] div[class*="x1ypdohk"]',  # Main content container
        'div[class*="x1xdureb"]',  # Post container
        'div[data-pressable-container="true"]',
        'article',
        'div[role="article"]'
    ]
    
    for selector in selectors:
        try:
            logger.info(f"Trying to find selector: {selector}")
            page.wait_for_selector(selector, timeout=15000)
            logger.info(f"Found selector: {selector}")
            return True
        except Exception as e:
            logger.debug(f"Selector {selector} not found: {str(e)}")
            continue
    
    return False

def parse_thread_content(element):
    """Parse a single thread element with improved selectors"""
    try:
        # Try multiple selectors for text content
        text_selectors = [
            'div[class*="x1xdureb"] div[class*="x1a6qonq"]',  # Main post content
            'span[class*="x1lliihq"][dir="auto"]',  # Text spans
            'div[class*="x126k92a"]',  # Content container
            'div[class*="xamitd3"] span'  # Text within interaction container
        ]
        
        text_content = ''
        for selector in text_selectors:
            elements = element.query_selector_all(selector)
            if elements:
                # Filter and combine text content
                contents = []
                for el in elements:
                    content = el.text_content().strip()
                    # Skip if content contains interaction text
                    if content and not any(x in content.lower() for x in ['like', 'comment', 'repost', 'share', 'more']):
                        contents.append(content)
                
                if contents:
                    text_content = ' '.join(contents)
                    break
        
        # Get username with improved selectors
        username = ''
        username_selectors = [
            'div[class*="x1pha0wt"] a[href^="/@"] span',
            'a[href^="/@"] span[class*="x1lliihq"]',
            'div[class*="xamitd3"] a[href^="/@"]'
        ]
        
        for selector in username_selectors:
            username_el = element.query_selector(selector)
            if username_el:
                username = username_el.text_content().strip()
                if username:
                    break
        
        if not username and (href_el := element.query_selector('a[href^="/@"]')):
            href = href_el.get_attribute('href')
            username = href.split('/@')[-1].split('/')[0]

        # Get metrics
        metrics = {
            'likes': '0',
            'replies': '0',
            'reposts': '0'
        }
        
        metric_selectors = {
            'likes': [
                'div[role="button"]:has-text("Like") span',
                'div[role="button"]:has-text("like") span'
            ],
            'replies': [
                'div[role="button"]:has-text("Reply") span',
                'div[role="button"]:has-text("reply") span'
            ],
            'reposts': [
                'div[role="button"]:has-text("Repost") span',
                'div[role="button"]:has-text("repost") span'
            ]
        }
        
        for metric, selectors in metric_selectors.items():
            for selector in selectors:
                try:
                    el = element.query_selector(selector)
                    if el:
                        value = el.text_content().strip()
                        if value.isdigit():
                            metrics[metric] = value
                        break
                except:
                    continue

        if not text_content or not username:
            return None

        # Get timestamp
        timestamp = None
        timestamp_selectors = [
            'time[datetime]',  # Selector langsung untuk elemen time
            'a[href*="/post/"] time',  # Time dalam link post
            'span.x1lliihq time',  # Time dalam span dengan class tertentu
            'div.x7a106z time', # Time dalam container posts
            # Selector spesifik untuk format timestamp yang Anda tunjukkan
            'span[class*="x1lliihq"][class*="x1plvlek"][class*="xryxfnj"] time',
            'span.x1lliihq.x1plvlek.xryxfnj time'
        ]
        
        for selector in timestamp_selectors:
            try:
                time_element = element.query_selector(selector)
                if time_element:
                    # Coba ambil timestamp dari atribut datetime
                    datetime_attr = time_element.get_attribute('datetime')
                    if datetime_attr:
                        timestamp = datetime_attr
                        break
                    
                    # Jika tidak ada atribut datetime, ambil text content
                    time_text = time_element.text_content().strip()
                    if time_text:
                        # Convert relative time ke timestamp
                        current_time = datetime.now()
                        if 'jam' in time_text:
                            hours = int(time_text.split()[0])
                            timestamp = (current_time - timedelta(hours=hours)).isoformat()
                        elif 'menit' in time_text:
                            minutes = int(time_text.split()[0])
                            timestamp = (current_time - timedelta(minutes=minutes)).isoformat()
                        elif 'detik' in time_text:
                            seconds = int(time_text.split()[0])
                            timestamp = (current_time - timedelta(seconds=seconds)).isoformat()
                        if timestamp:
                            break
            except Exception as e:
                logger.debug(f"Error getting timestamp with selector {selector}: {str(e)}")
                continue

        # If no timestamp found, use current time
        if not timestamp:
            timestamp = datetime.now().isoformat()

        return {
            "text": text_content,
            "username": username,
            "likes": metrics['likes'],
            "replies": metrics['replies'],
            "reposts": metrics['reposts'],
            "timestamp": timestamp,
            "scraped_at": datetime.now().isoformat()
        }

    except Exception as e:
        logger.error(f"Error parsing thread element: {str(e)}")
        return None

def is_within_timeframe(timestamp_str: str, days: int = 1) -> bool:
    """Check if timestamp is within specified days from now"""
    try:
        post_time = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
        cutoff_time = datetime.now(post_time.tzinfo) - timedelta(days=days)
        return post_time >= cutoff_time
    except Exception as e:
        logger.error(f"Error parsing timestamp {timestamp_str}: {str(e)}")
        return False

def scrape_threads_search(search_term: str, max_posts: int = 1000, days_back: int = 1) -> List[Dict]:
    """Scrape Threads posts with time filtering"""
    logger.info(f"Starting search for: {search_term}, looking back {days_back} days")
    
    collected_posts = []
    seen_posts = set()
    old_posts_count = 0  # Counter for posts outside timeframe
    
    with sync_playwright() as pw:
        try:
            browser = pw.chromium.launch(
                headless=False,
                args=['--no-sandbox']
            )
            
            context = browser.new_context(
                viewport={"width": 1280, "height": 720},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            )
            
            page = context.new_page()
            
            # Navigate directly to sorted search URL
            encoded_term = quote(search_term)
            # Add sort parameter for latest posts
            search_url = f"https://www.threads.net/search?q={encoded_term}&t=recent"
            
            logger.info(f"Navigating to search URL: {search_url}")
            page.goto(search_url)
            time.sleep(3)
            
            # Handle login if needed
            if click_login_button(page):
                if not perform_threads_login(page):
                    raise Exception("Failed to login to Threads")
                    
                # Return to search page after login
                logger.info("Returning to search results...")
                page.goto(search_url)
                time.sleep(5)
            
            # Wait for content with improved handling
            if not wait_for_threads_content(page):
                logger.error("Could not find content after multiple attempts")
                return collected_posts
            
            scroll_count = 0
            last_height = 0
            consecutive_same_height = 0
            consecutive_old_posts = 0  # Counter for consecutive posts outside timeframe
            
            while len(collected_posts) < max_posts and scroll_count < 50:
                try:
                    # Try multiple selectors for thread elements
                    thread_elements = []
                    element_selectors = [
                        'div[class*="x1ypdohk"][data-pressable-container="true"]',
                        'div[class*="x78zum5"] div[class*="x1xdureb"]',
                        'article',
                        'div[role="article"]'
                    ]
                    
                    for selector in element_selectors:
                        thread_elements = page.query_selector_all(selector)
                        if thread_elements:
                            logger.info(f"Found {len(thread_elements)} threads with selector: {selector}")
                            break
                    
                    if not thread_elements:
                        logger.warning("No thread elements found, retrying after scroll...")
                        page.evaluate('window.scrollTo(0, window.scrollY + 300)')
                        time.sleep(2)
                        continue
                    
                    # Process threads
                    old_posts_in_batch = 0
                    for element in thread_elements:
                        if len(collected_posts) >= max_posts:
                            break
                            
                        post_data = parse_thread_content(element)
                        
                        if post_data and post_data["text"] and post_data["timestamp"]:
                            # Check if post is within timeframe
                            if not is_within_timeframe(post_data["timestamp"], days_back):
                                old_posts_in_batch += 1
                                old_posts_count += 1
                                continue
                                
                            post_id = f"{post_data['username']}:{post_data['text'][:50]}"
                            
                            if post_id not in seen_posts:
                                seen_posts.add(post_id)
                                collected_posts.append(post_data)
                                logger.info(f"Collected {len(collected_posts)} posts...")
                    
                    # Check if we're seeing too many old posts
                    if old_posts_in_batch > 0:
                        consecutive_old_posts += 1
                        if consecutive_old_posts >= 3:
                            logger.info("Found too many old posts, stopping collection")
                            break
                    else:
                        consecutive_old_posts = 0
                    
                    # Scroll with improved handling
                    last_height = page.evaluate('document.body.scrollHeight')
                    page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
                    time.sleep(3)
                    
                    new_height = page.evaluate('document.body.scrollHeight')
                    if new_height == last_height:
                        consecutive_same_height += 1
                        if consecutive_same_height >= 3:
                            logger.info("Reached end of scrollable content")
                            break
                    else:
                        consecutive_same_height = 0
                    
                    scroll_count += 1
                    
                except Exception as e:
                    logger.error(f"Error during scrolling: {str(e)}")
                    break
            
            logger.info(f"Collection completed. Found {old_posts_count} posts outside timeframe")
            # Sort posts by timestamp, newest first
            collected_posts.sort(key=lambda x: x['timestamp'], reverse=True)
            return collected_posts[:max_posts]
            
        except Exception as e:
            logger.error(f"Error during scraping: {str(e)}")
            return collected_posts
        finally:
            if 'browser' in locals():
                browser.close()

def save_to_csv(posts: List[Dict], search_term: str):
    """Save collected posts to CSV file with improved error handling"""
    import pandas as pd
    
    if not posts:
        logger.warning("No posts to save")
        return None
    
    try:
        df = pd.DataFrame(posts)
        
        # Convert timestamp to datetime for better sorting
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        # Sort by timestamp descending (newest first)
        df = df.sort_values('timestamp', ascending=False)
        
        # Ensure all expected columns exist
        expected_columns = ['text', 'username', 'likes', 'replies', 'reposts', 'timestamp', 'scraped_at']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns
        df = df.reindex(columns=expected_columns)
        column_mapping = {
            'timestamp': 'Date', 
            'username': 'User', 
            'text': 'Text',
            'replies': 'Replies',
            'reposts': 'Reposts',
            'likes' : 'Likes',
            'scraped_at': 'Scraped At'
        }
        mapping_df = rename_columns(df, column_mapping)
        mapping_df['Platform'] = 'Threads'
        return mapping_df
            
    except Exception as e:
        logger.error(f"Error saving to CSV: {str(e)}")
        return None

