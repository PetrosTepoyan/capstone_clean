
from ConcreteScrapers.Bnakaran.BnakaranScrapingPipeline import BnakaranScrapingPipeline
from ConcreteScrapers.Bnakaran.BnakaranApartmentScraper import BnakaranApartmentScraper
from Protocols import ApartmentScrapingPipeline
from Services import ImageLoader
import requests
import re
import logging
import xml.etree.ElementTree as ET

class BnakaranSitemapScrapingPipeline(ApartmentScrapingPipeline):

    def __init__(self, sitemap_url, storage, image_loader: ImageLoader):
        self.base_url = sitemap_url
        self.page = 1
        self.finished_with_sitemap = False
        self.storage = storage
        self.image_loader = image_loader

        # Initialize an empty list to store the filtered URLs
        filtered_urls = []

        try:
            # Fetch the sitemap
            response = requests.get(sitemap_url)

            # Check if the request was successful
            if response.status_code == 200:
                # Parse the XML
                root = ET.fromstring(response.content)

                # Regex pattern to match URLs ending with -d<number>
                pattern = re.compile(r".*-d\d+$")

                # Extract URLs matching the pattern
                filtered_urls = [elem.text for elem in root.findall(".//{http://www.sitemaps.org/schemas/sitemap/0.9}loc")
                                if pattern.match(elem.text)]

        except Exception as e:
            error_message = str(e)
            logging.critical(error_message)
        
        self.links = [link for link in filtered_urls if "apartment" in link]

        super().__init__(BnakaranApartmentScraper)

    def navigate_to_next_page(self):
        self.finished_with_sitemap = True

    def scrape_apartment(self, apartment_url):
        BnakaranScrapingPipeline.scrape_apartment(self, apartment_url)

    def get_apartment_links(self):
        if self.finished_with_sitemap:
            return []
        else:
            return self.links

    def get_base_link(self) -> str:
        return "https://www.bnakaran.com"