import requests
from bs4 import BeautifulSoup
from ConcreteStorages.CSVStorage import CSVStorage
from ConcreteScrapers.Bars.BarsApartmentScraper import BarsApartmentScraper
from Protocols import ApartmentScrapingPipeline
from Services import ImageLoader
import logging
from time import sleep

import pandas as pd

# https://bars.am/en/properties/standard/apartment
class BarsApartmentScrapingPipeline(ApartmentScrapingPipeline):

    def __init__(self, base_url, storage: CSVStorage, image_loader: ImageLoader):
        self.base_url = base_url
        self.page = 1
        self.storage = storage
        self.image_loader = image_loader

        self.__set_soup(base_url)
        super().__init__(BarsApartmentScraper)

    def navigate_to_next_page(self):
        self.navigate_to_next_page_()
        
    def navigate_to_next_page_(self):
        self.page += 1
        self.__set_soup(self.base_url)

    def scrape_apartment(self, apartment_url):
        
        id = self.apartment_scraper.get_id(apartment_url)
        
        # Create an instance of ApartmentScraper with the provided URL
        apartment_scraper: BarsApartmentScraper = self.apartment_scraper(apartment_url)

        # Call the scrape method of the ApartmentScraper
        apartment_scraper.scrape()
        apartment_data = apartment_scraper.values()

        # Store or process the scraped data as needed
        self.storage.append(apartment_data)
        
        # download images
        images_links = apartment_scraper.images_links()
        if self.image_loader:
            self.image_loader.download_images(
                links = images_links,
                source = BarsApartmentScraper.source_identifier(),
                apartment_id = apartment_scraper.id
            )

    def get_apartment_links(self, page_url=None):
        if page_url is None:
            page_url = self.base_url

        # Find all 'a' elements with the specific class
        a_elements = self.soup.find_all('a', class_='wrapper-image')

        # Iterate over the found 'a' elements and navigate to their links
        links = []
        for a_element in a_elements:
            link = a_element.get('href')
            links.append(link)

        return links
    
    def __set_soup(self, url, retry_count: int = 0):
        # Send a GET request to the website
        body = {
            'offset': str(self.page),
            'category': 'apartment',
            'cx8v78cx7': 'xc90v8cx8vcxv',
            'section': 'standard',
            'for': 'sale',
            'price_type': 'sale_total_price',
            'price_from': '',
            'price_to': '',
            'currency_select': 'USD',
            'city[]': '1',
            'code': '',
            'house_flat_area_sqm_from': '',
            'house_flat_area_sqm_to': '',
            'land_area_sqm_from': '',
            'land_area_sqm_to': '',
            'rooms_from': '',
            'rooms_to': ''
        }


        response = requests.post(url, data = body)

        # Check if the page is empty or not found, and break the loop if so
        if response.status_code != 200:
            error = f"Bars | Failed to fetch the webpage. Status code: {response.status_code}, {url}"
        
            if retry_count < 3:
                sleep(retry_count + 1)
                self.__set_soup(url, retry_count + 1)
                return
            else:
                logging.critical(error)
                raise Exception(error)
            

        # Parse the HTML content of the page with BeautifulSoup
        self.soup = BeautifulSoup(response.text, 'html.parser')
        
    def finish(self):
        self.driver.quit()