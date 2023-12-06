import re
import logging
import requests
from bs4 import BeautifulSoup
from Protocols import ApartmentScraper

class MyRealtyApartmentScraper(ApartmentScraper):
    
    def __init__(self, webpage: str):
        
        self.webpage = webpage
        # Send a GET request to the website
        response = requests.get(webpage)

        # Check if the page is empty or not found, and break the loop if so
        if response.status_code != 200 or not response.text.strip():
            print("Failed", response.status_code)

        # Parse the HTML content of the page with BeautifulSoup
        self.soup = BeautifulSoup(response.text, 'html.parser')
        
        self.id = None
        self.price = None
        self.facilities = None
        self.address = None
        self.area = None
        self.room = None
        self.floor = None
        self.storeys = None
        self.building_type = None
        self.ceiling_height = None
        self.condition = None
        self.bathroom = None
        self.added_in_date = None
        self.view_count = None
        
        
    def get_id(webpage: str) -> str:
        return webpage.split("/")[-1]
        
    @staticmethod
    def source_identifier():
        return "myrealty"
    
    # must through some errors
    def scrape(self):
        try: 
            success = self.__scrape_id()
        except:
            logging.error("code: 012 | ID")
        
        if success:
            self.__scrape_price()
            
            try:
                self.__scrape_facilities()
            except:
                logging.error("code: 012 | Facilities")
                
            self.__scrape_location()
                
            try:
                self.__scrape_misc()
            except:
                logging.error("code: 012 | misc")
                
            try:
                self.__scrape_misc_2()
            except:
                logging.error("code: 012 | misc2")
                
            try:
                self.__scrape_added_in_date()
            except:
                logging.error("code: 012 | added in date")
                
            try: 
                self.__scrape_look_count()
            except:
                logging.error("code: 012 | view count")
                
        else:
            logging.error("code: 012 | ID")
            
    def values(self):
        return {
            "source" : MyRealtyApartmentScraper.source_identifier(),
            "webpage" : self.webpage,
            "id": self.id,
            "price" : self.price,
            "facilities" : self.facilities,
            "location" : self.address,
            "area" : self.area,
            "rooms" : self.room,
            "floor" : self.floor,
            "storeys" : self.storeys,
            
            "building_type" : self.building_type,
            "bathroom_count" : self.bathroom,
            "ceiling_height" : self.ceiling_height,
            "condition" : self.condition,
            
            "added_in_date" : self.added_in_date,
            "view_count" : self.view_count
        }
        # need to scrape bathroom count, building type, ceiling height, condition
        
    def images_links(self) -> list[str]:
        # Extract image URLs
        # Find img elements with the specific classes
        img_elements = self.soup.find_all('img', class_=['owl-lazy', 'lazy-loaded'])

        # Extract the src attribute of the img elements
        img_urls: list[str] = list(set([img['data-src'] for img in img_elements if 'data-src' in img.attrs]))
        return img_urls
    
    def __scrape_id(self) -> bool:
        # Find the div with the specific class and extract the ID
        id_div = self.soup.find('div', class_ = 'item-view-id')
        id_text = id_div.get_text(strip = True)  # Get the text content of the div
        id_number = id_text.split()[-1]  # Split the text and get the last part, which is the ID number
        
        if id_number is None:
            return False
        else:
            self.id = id_number
            return True
        
    def __scrape_facilities(self):
        facilities = [li.find('label').get_text() for li in self.soup.find_all('li', class_='col-sm-6 col-lg-4 col-xl-3 mb-1')]
        self.facilities = facilities

    def __scrape_price(self):
        price_element = self.soup.find('div', class_='pl-0')
        if price_element:
            price_element_text = price_element.get_text(strip = True)
            price_text_stripped = price_element_text.split("/")[0]
            price_text_stripped = price_text_stripped.replace(",", "")
            price = int(price_text_stripped)
            self.price = price
            
    def __scrape_location(self):
        # Find the div with the specific id
        div_tag = self.soup.find('div', id = 'yandex_map_item_view')

        # Extract the latitude and longitude from the data-lat and data-lng attributes
        latitude = div_tag['data-lat']
        longitude = div_tag['data-lng']
        self.latitude = latitude
        self.longitude = longitude
        
        address_div = self.soup.find('div', class_='col-auto item-view-address d-none d-xl-block mr-0')

        # Extract the text within the div element
        address = address_div.get_text(strip=True)
        self.address = address

        
    def __scrape_misc(self):
        # Find the parent div with the specific class
        parent_div = self.soup.find('div', class_='col-12 d-flex justify-content-between justify-content-sm-start item-view-price-params')

        # Extract the area, room, floor, and storeys
        area = parent_div.find('div', class_='pl-0').find('span').text
        room = parent_div.find_all('div')[1].find('span').text
        floor_storeys = parent_div.find_all('div')[2].find('span').text
        floor, storeys = floor_storeys.split('/')

        self.area = self.__extract_first_number(area)
        self.room = self.__extract_first_number(room)
        self.floor = self.__extract_first_number(floor)
        self.storeys = self.__extract_first_number(storeys)
        
    def __scrape_misc_2(self):
        values = {}

        # Find the relevant <li> elements and extract the values
        for li in self.soup.find_all('li', class_='row d-flex align-items-center no-gutters'):
            label = li.find('label').get_text()
            value = li.find('div', class_='col-5').find('span').get_text(strip=True)
            values[label] = value
        # Extracted values
        self.bathroom = values.get("Bathroom")
        self.building_type = values.get("Building type")
        self.ceiling_height = values.get("Ceiling height")
        self.condition = values.get("condition")

    def __scrape_added_in_date(self):
        # Find the 'Added in' date
        added_in_div = self.soup.find('div', class_='col-auto mb-1')
        added_in_date = added_in_div.get_text(strip=True).split()[-1]
        self.added_in_date = re.sub(r'[^\d\.]', '', added_in_date)
        
    def __scrape_look_count(self):
        view_count_span = self.soup.find('span', class_='item-view-count')
        view_count = view_count_span.get_text(strip=True)
        self.view_count = int(view_count)
        
    def __extract_first_number(self, s):
        match = re.search(r'\d+', s)
        return int(match.group(0)) if match else None