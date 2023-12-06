import re
import requests
import logging
from bs4 import BeautifulSoup
from Protocols import ApartmentScraper

class BnakaranApartmentScraper(ApartmentScraper):
    
    def __init__(self, webpage: str):
        # Send a GET request to the website
        response = requests.get(webpage)
        
        # Check if the page is empty or not found, and break the loop if so
        if response.status_code != 200 or not response.text.strip():
            error = f"Failed to fetch the webpage. Status code: {response.status_code}, {webpage}"
            logging.error(error)
            raise Exception(error)
        
        # Parse the HTML content of the page with BeautifulSoup
        self.webpage = webpage
        self.soup = BeautifulSoup(response.content, 'html.parser')
        self.id = webpage.split("-")[-1]
    
    def get_id(webpage: str) -> str:
        return webpage.split("-")[-1]
    
    @staticmethod
    def source_identifier():
        return "bnakaran"
    
    def scrape(self):
        self.__scrape_features()
        self.__scrape_location()
        self.__scrape_details()
        self.__scrape_room_details()
        self.__scrape_additional_features()
        self.__scrape_utilities()
        self.__scrape_added_in_date()
        self.__scrape_visit_count()
        self.__scrape_price()
    
    def values(self):
        
        apartment_data = {
            "source" : BnakaranApartmentScraper.source_identifier(),
            "webpage" : self.webpage,
            "id" : self.id,
            "price" : self.price,
            "area": self.area,
            "storeys": self.storeys,
            "floor": self.floor,
            "rooms": self.rooms,
            "latitude": self.latitude,
            "longitude": self.longitude,
            # "details": self.details,
            "construction_type":self.details.get("Construction type", None),
            "building_type":self.details.get('Building type', None),
            "renovation":self.details.get('Renovation', None),
            "flooring": self.details.get('Flooring', None),
            "entrance_door":self.details.get('Entrance door', None),
            "windows" : self.details.get("Windows", None),
            "heating" : self.details.get('Heating', None),
            "cooling" : self.details.get("Cooling", None),
            "parking" : self.details.get('Parking', None),
            
            "room_details": self.room_details,
            "additional_features": self.additional_features,
            "added_in_date": self.added_in_date,
            "visit_count": self.visited_count,
            "utilities": self.utilities
        }
        return apartment_data

        
    def images_links(self) -> list[str]:
        return [a['href'] for a in self.soup.find_all('a', class_='item', href=True)]
    
    def __flatten_json(self, apartment_data):
        # Extract the nested JSON fields
        details = apartment_data.pop('details', {})
        room_details = apartment_data.pop('room_details', {})

        # Merge the nested dictionaries into the main one
        # Note: If there are overlapping keys, the keys from the later dictionaries will overwrite those from the earlier ones
        flattened_data = {**apartment_data, **details, **room_details}
        
        return flattened_data

    def __scrape_features(self):
        for li in self.soup.select('ul.property-main-features > li'):
            key = li.get_text(strip=True).split(':')[0].strip().lower()
            value = li.find('span').get_text(strip=True)
            if key == 'area':
                self.area = int(''.join(filter(str.isdigit, value)))
            elif key == 'storey':
                vals = [int(s.strip()) for s in value.split("/")]
                self.storeys = vals[1]
                self.floor = vals[0]
            elif key == 'rooms':
                self.rooms = int(''.join(filter(str.isdigit, value)))
    
    def __scrape_location(self):
        yandex_map_div = self.soup.find('div', class_='yandex-map')
        if yandex_map_div:
            self.latitude = yandex_map_div.get('data-y')
            self.longitude = yandex_map_div.get('data-x')
        else:
            logging.error("Yandex map element not found on the page.")
    
    def __scrape_details(self):
        self.details = {}
        property_features = self.soup.find('ul', class_='property-features').find_all('li', recursive=False)
        for feature in property_features:
            parts = feature.get_text(strip=True).split(':')
            if len(parts) >= 2:
                key, value = parts[0].strip(), parts[1].strip()
                self.details[key] = value
                
    def __scrape_utilities(self):
        # Find all <li> elements within the specified <ul> class
        li_elements = self.soup.select('ul.property-features margin-top-0 li')

        # Extract the text before ":" in each <li> element and store it in a list
        property_features = [li.get_text(strip=True).split(':')[0] for li in li_elements]
        self.utilities = property_features
    
    def __scrape_room_details(self):
        features_lists = self.soup.find_all('ul', class_='property-features')
        if len(features_lists) > 1:
            room_features_list = features_lists[1].find_all('li', recursive=False)
            self.room_details = {}
            for feature_item in room_features_list:
                parts = feature_item.get_text(strip=True).split(':')
                if len(parts) >= 2:
                    key, value = parts[0].strip(), parts[1].strip()
                    self.room_details[key] = value
        else:
            logging.error("The expected room details section was not found")
    
    def __scrape_additional_features(self):
        features_list = self.soup.find('ul', class_='property-features checkboxes margin-top-0')
        if features_list:
            feature_items = features_list.find_all('li', recursive=False)
            self.additional_features = [feature.get_text(strip=True) for feature in feature_items]
        else:
            logging.error("Additional features information is not available.")
            
    def __scrape_added_in_date(self):
        stats = self.soup.find('ul', class_='property-stats')
        updated_date = stats.find_all('li')[0].find('span').text.strip()
        self.added_in_date = updated_date

    def __scrape_visit_count(self):
        stats = self.soup.find('ul', class_='property-stats')
        visited_count = stats.find_all('li')[2].find('span').text.strip()
        self.visited_count = visited_count

    def __scrape_price(self):
        # Prices
        prices = self.soup.find('ul', class_='property-prices')
        sale_price = prices.find('li').find('span').text.strip()
        is_in_drams = "Դ" in sale_price 
        self.price = int(re.sub(r'\D', '', sale_price))
            
        if is_in_drams:
            self.price = self.price / 400