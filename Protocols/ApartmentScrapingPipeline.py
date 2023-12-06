from abc import ABC, abstractmethod
from Protocols import ApartmentScraper

class ApartmentScrapingPipeline(ABC):
    
    def __init__(self, apartment_scraper: ApartmentScraper):
        """
        Constructor that takes an type of ApartmentScraper as an argument.

        Args:
            apartment_scraper (ApartmentScraper): An type of ApartmentScraper to be used for scraping.
        """
        self.apartment_scraper = apartment_scraper
        self.page_count = 0
        self.repeat_count = 0

    @abstractmethod
    def get_apartment_links(self, page_url: str):
        """
        Abstract method for getting links to individual apartments on a page.
        Subclasses must implement this method.

        Args:
            page_url (str): The URL of the page containing apartment links.

        Returns:
            list: A list of apartment URLs.
        """
        pass

    @abstractmethod
    def scrape_apartment(self, apartment_url: str):
        """
        Abstract method for scraping data from an individual apartment page.
        Subclasses must implement this method.

        Args:
            apartment_url (str): The URL of the apartment page to scrape.

        Returns:
            dict: A dictionary containing scraped data.
        """
        pass

    @abstractmethod
    def navigate_to_next_page(self):
        """
        Abstract method for navigating to the next page of apartment listings.
        Subclasses must implement this method.
        """
        self.page_count += 1


    
    def scrape_links(self, links):
        for link in links:
            self.scrape_apartment(link)