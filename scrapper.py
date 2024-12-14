import os
import time
from typing import List, Dict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

class WebScraper:
    def __init__(self, chromedriver_path: str):
        """
        Initialize the web scraper with Chrome WebDriver configuration
        
        Args:
            chromedriver_path (str): Full path to the ChromeDriver executable
        """
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        
        self.service = Service(chromedriver_path)
        self.driver = None
        
    def setup_driver(self):
        """
        Set up and return a configured Chrome WebDriver
        
        Returns:
            WebDriver: Configured Chrome WebDriver
        """
        self.driver = webdriver.Chrome(service=self.service, options=self.chrome_options)
        return self.driver
    
    def wait_for_element(self, locator: tuple, timeout: int = 10):
        """
        Wait for an element to be present
        
        Args:
            locator (tuple): Selenium locator tuple
            timeout (int): Maximum wait time in seconds
        
        Returns:
            WebElement: The located element
        """
        return WebDriverWait(self.driver, timeout).until(
            EC.presence_of_element_located(locator)
        )
    
    def extract_image_links(self) -> List[str]:
        """
        Extract links from images on the page
        
        Returns:
            List[str]: List of image links
        """
        try:
            image_elements = self.driver.find_elements(By.TAG_NAME, 'img')
            image_links = [
                img.get_attribute('src') or img.find_element(By.XPATH, '..').get_attribute('href')
                for img in image_elements
            ]
            return [link for link in image_links if link and link.startswith('http')]
        except Exception as e:
            print(f"Error extracting image links: {e}")
            return []
    
    def extract_page_details(self) -> Dict[str, str]:
        """
        Extract comprehensive page details
        
        Returns:
            Dict[str, str]: Dictionary containing page details
        """
        details = {
            'title': self.driver.title,
            'url': self.driver.current_url,
            'page_content': self.driver.find_element(By.TAG_NAME, 'body').text
        }
        return details
    
    def navigate_and_extract(self, url: str, max_depth: int = 2):
        """
        Navigate through pages, extract details and follow links
        
        Args:
            url (str): Starting URL
            max_depth (int): Maximum depth of link traversal
        
        Returns:
            List[Dict]: List of extracted page details
        """
        scraped_pages = []
        visited_urls = set()
        
        def recursive_scrape(current_url: str, current_depth: int):
            if current_depth > max_depth or current_url in visited_urls:
                return
            
            try:
                self.driver.get(current_url)
                time.sleep(2)  # Allow page to load
                
                # Extract page details
                page_details = self.extract_page_details()
                scraped_pages.append(page_details)
                visited_urls.add(current_url)
                
                # Extract image links
                image_links = self.extract_image_links()
                
                # Recursively follow links
                for link in image_links:
                    recursive_scrape(link, current_depth + 1)
                
            except Exception as e:
                print(f"Error scraping {current_url}: {e}")
        
        recursive_scrape(url, 0)
        return scraped_pages
    
    def save_scraped_data(self, scraped_data: List[Dict], output_file: str = 'scraped_data.txt'):
        """
        Save scraped data to a text file
        
        Args:
            scraped_data (List[Dict]): List of scraped page details
            output_file (str): Output file path
        """
        with open(output_file, 'w', encoding='utf-8') as f:
            for index, page in enumerate(scraped_data, 1):
                f.write(f"Page {index}:\n")
                f.write(f"Title: {page['title']}\n")
                f.write(f"URL: {page['url']}\n")
                f.write(f"Content: {page['page_content'][:1000]}...\n\n")
    
    def close(self):
        """
        Close the WebDriver
        """
        if self.driver:
            self.driver.quit()

def main():
    # ChromeDriver path - modify this to your specific path
    chromedriver_path = r'C:\Users\HAMZA\Downloads\Compressed\chromedriver-win64\chromedriver.exe'
    
    # URL to scrape
    page_url = 'https://wilsoncombat.com/long-guns/ar-10-calibers/358-winchester.html'
    
    try:
        # Initialize scraper
        scraper = WebScraper(chromedriver_path)
        scraper.setup_driver()
        
        # Scrape data with max depth of 2
        scraped_data = scraper.navigate_and_extract(page_url, max_depth=2)
        
        # Save scraped data
        scraper.save_scraped_data(scraped_data)
        
        print(f"Scraped {len(scraped_data)} pages successfully!")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    
    finally:
        scraper.close()

if __name__ == "__main__":
    main()