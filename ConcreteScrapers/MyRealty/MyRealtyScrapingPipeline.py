import requests
from bs4 import BeautifulSoup
from ConcreteScrapers.MyRealty.MyRealtyApartmentScraper import MyRealtyApartmentScraper
from Protocols import ApartmentScrapingPipeline
from Services import ImageLoader
from Protocols import Storage
import logging
import pandas as pd

class MyRealtyScrapingPipeline(ApartmentScrapingPipeline):

    def __init__(self, base_url: str, storage: Storage, image_loader: ImageLoader):
        self.base_url = base_url
        self.page = 1
        self.storage = storage
        self.image_loader = image_loader
        
        self.__set_soup(base_url)
        super().__init__(MyRealtyApartmentScraper)

    def __set_soup(self, url: str):
        # Send a GET request to the website
        response = requests.get(url)

        # Check if the page is empty or not found, and break the loop if so
        if response.status_code != 200 or not response.text.strip():
            error = f"MyRealty | Failed to fetch the webpage. Status code: {response.status_code}, {url}"
            logging.critical(error)
            raise Exception(error)

        # Parse the HTML content of the page with BeautifulSoup
        self.soup = BeautifulSoup(response.text, 'html.parser')

    def navigate_to_next_page(self):
        self.page += 1
        self.__set_soup(f"{self.base_url}?page={self.page}")

    def scrape_apartment(self, apartment_url):
        
        id = self.apartment_scraper.get_id(apartment_url)
        
        # Create an instance of ApartmentScraper with the provided URL
        apartment_scraper: MyRealtyApartmentScraper = self.apartment_scraper(apartment_url)
        
        # Call the scrape method of the ApartmentScraper
        apartment_scraper.scrape()
        apartment_data = apartment_scraper.values()

        # Store or process the scraped data as needed
        self.storage.append(apartment_data)  # Replace with your storage mechanism
        
        # download images
        images_links = apartment_scraper.images_links()
        if self.image_loader:
            self.image_loader.download_images(
                links = images_links,
                source = MyRealtyApartmentScraper.source_identifier(),
                apartment_id = apartment_scraper.id
            )

    def get_apartment_links(self, page_url=None):
        if page_url is None:
            page_url = self.base_url

        # Find all 'a' elements with the specific class
        a_elements = self.soup.find_all('a', class_='btn btn-pink-transparent btn-cs text-uppercase item-more-btn ml-auto')

        # Iterate over the found 'a' elements and navigate to their links
        links = []
        for a_element in a_elements:
            link = a_element.get('href')
            links.append(link)

        return links