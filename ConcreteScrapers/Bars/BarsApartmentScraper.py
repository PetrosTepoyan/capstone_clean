import re
import requests
from bs4 import BeautifulSoup
from Protocols import ApartmentScraper
import logging

class BarsApartmentScraper(ApartmentScraper):
    
    def __init__(self, webpage: str):
        
        response = requests.get(webpage)

        if response.status_code != 200 or not response.text.strip():
            print("Failed", response.status_code)
        self.webpage = webpage
        self.soup = BeautifulSoup(response.text, 'html.parser')
        
        self.id = self.webpage.split("/")[-1]
        self.price = None
        self.facilities = None
        self.address = None
        self.area = None
        self.rooms = None
        self.floor = None
        self.storeys = None
        self.bedrooms = None
        self.bathrooms = None
        self.ceiling_height = None
        self.building_type = None
        self.condition = None

    def get_id(webpage: str) -> str:
        return webpage.split("/")[-1]
        
    @staticmethod
    def source_identifier():
        return "bars"
        
    # must through some errors
    def scrape(self):
        
        # Set a check on Capcha and if detected, use `prompt` from Python to 
        # wait for the user to pass it.
        
        captcha_div = self.soup.find('div', class_='captcha_absolute')
        if captcha_div:
            _ = input("Detected captcha. Please, pass it and press input anything here.")
            response = requests.get(self.webpage)
            self.soup = BeautifulSoup(response.text, 'html.parser')
        
        self.price = self.__get_price()
        self.facilities = self.__get_facilities()
        self.address = self.__get_address()
        self.area = self.__get_quick_data("Apartment area (sq/m):", float)
        self.rooms = self.__get_quick_data("Number of rooms:", int)
        self.floor = self.__get_quick_data("Floor:", int)
        self.storeys = self.__get_quick_data("Floors:", int)
        
        self.bedrooms = self.__get_quick_data("Number of bedrooms:", int)
        self.bathrooms = self.__get_quick_data("Number of bathrooms:", int)
        self.ceiling_height = self.__get_quick_data("Ceiling height (m):", float) 
        self.building_type = self.__get_quick_data("Building Type:", str)
        self.condition = self.__get_quick_data("Condition:", str)
        
        
    def values(self):
        return {
            "source" : BarsApartmentScraper.source_identifier(),
            "webpage" : self.webpage,
            "id": self.id,
            "price" : self.price,
            "facilities" : self.facilities,
            "location" : self.address,
            "area" : self.area,
            "rooms" : self.rooms,
            "floor" : self.floor,
            "storeys" : self.storeys,
            
            "bedrooms" : self.bedrooms,
            "bathroom_count" : self.bathrooms,
            "ceiling_height" : self.ceiling_height,
            "building_type" : self.building_type,
            "condition" : self.condition
        }
        
    def images_links(self) -> list[str]:
        image_links = [img['src'] for img in self.soup.findAll('img')]
        final_links = []
        for link in image_links:
            if "uploads/listing-pics/" in link and "_" not in link:
                final_links.append(link)
        return final_links
    
    def __get_quick_data(self, label: str, type_) -> any:
        try:
            quick_data_tag = self.soup.find('strong', text=f'{label}').parent
            quick_data_text = ''.join(quick_data_tag.stripped_strings).replace(f'{label}', '').strip()
        except:
            logging.error(f"code: 012 | {label}")
            return None
        return type_(quick_data_text)
        
    def __get_address(self) -> str:
        # Find the div tag with the specific id "listing-address-label"
        div_tag = self.soup.find('div', id="listing-address-label")

        # If the tag is found, extract the text content after the icon
        if div_tag:
            address = div_tag.text.replace('<i class="fa fa-map-marker"></i>', '').strip()
            return address
        else:
            return None
        
    def __get_price(self) -> int:
        # Find the div tag with the specific class "price for-sale-2"
        div_tag = self.soup.find('div', class_="price for-sale-2")

        # If the tag is found, extract the text content after the icon
        if div_tag:
            price = div_tag.text.replace('<i class="fa fa-usd"></i>', '').strip().replace(",", "")
            return int(price)
        else:
            return None
        
    def __get_facilities(self) -> list:
        amenities = [item.span.text for item in self.soup.findAll('li', class_='amenities-item')]
        return amenities