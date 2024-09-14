import requests
from bs4 import BeautifulSoup
from utils import get_embedding, pinecone_index
import time
import logging
from threading import Thread

# Set up logging
logging.basicConfig(filename='scraping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Function to scrape data from a given URL
def scrape_articles(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            articles = soup.find_all('article')  # Modify based on the site's structure

            scraped_data = []
            for article in articles:
                title = article.find('h2').get_text()
                link = article.find('a')['href']
                summary = article.find('p').get_text()
                
                # Collect scraped data
                scraped_data.append({
                    'title': title,
                    'link': link,
                    'summary': summary
                })
            
            logging.info(f"Scraped {len(scraped_data)} articles from {url}")
            return scraped_data
        else:
            logging.error(f"Failed to scrape {url}, status code: {response.status_code}")
            return []
    except Exception as e:
        logging.error(f"Error scraping {url}: {str(e)}")
        return []

# Function to update Pinecone with scraped data
def update_pinecone(scraped_data):
    for item in scraped_data:
        text = f"{item['title']} {item['summary']}"
        embedding = get_embedding(text)
        
        # Insert the embedding into Pinecone
        pinecone_index.upsert([
            {"id": item['link'], "values": embedding.flatten().tolist()}
        ])
        logging.info(f"Updated Pinecone index with article: {item['title']}")

# Function to scrape and update Pinecone based on user-provided site details
def scrape_and_update_site(url):
    scraped_data = scrape_articles(url)
    if scraped_data:
        update_pinecone(scraped_data)
        logging.info(f"Successfully scraped and updated Pinecone for {url}")
    else:
        logging.warning(f"No data scraped from {url}")

# Background scraping with user-provided URL
def run_scraping_task(url):
    while True:
        scrape_and_update_site(url)
        logging.info(f"Scraping task completed for {url}. Sleeping for 1 hour.")
        time.sleep(3600)  # Scrape every hour (adjust as needed)

# Function to start the scraping thread for a specific site
def start_scraping_thread(url):
    thread = Thread(target=run_scraping_task, args=(url,))
    thread.daemon = True  # Daemon thread will exit when the main program exits
    thread.start()
    logging.info(f"Started background scraping thread for {url}")
