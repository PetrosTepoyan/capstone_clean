from abc import ABC, abstractmethod

class ApartmentScraper(ABC):
    @abstractmethod
    def scrape(self):
        """
        Abstract method for scraping the current page of an individual apartment.
        Subclasses must implement this method.
        """
        pass

    @abstractmethod
    def values(self):
        """
        Abstract method for returning a dictionary with keys and values scraped from the apartment page.
        Subclasses must implement this method.
        """
        pass
    
    @staticmethod
    @abstractmethod
    def source_identifier() -> str:
        pass

    @abstractmethod
    def images_links(self) -> list[str]:
        pass
    
    @abstractmethod
    def get_id(webpage: str) -> str:
        pass