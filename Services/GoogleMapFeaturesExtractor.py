import time
import math
import requests
from urllib.parse import quote
from VirtualModels.Amenity import Amenity

# WILL NOT BE USED
class GeoFeaturesExtractor:
    BASE_URL = "https://maps.googleapis.com/maps/api/"
    API_KEY = "AIzaSyAfDtObYwES7ePyjfXVl-7Govd_U6_5_dk"

    def __init__(self, types_to_include, radius):
        self.types_to_include = set(types_to_include)
        self.radius = radius

    def location(self, input):
        
        parameters = {
            'fields': 'geometry',
            'input': input,
            'inputtype': 'textquery',
            'key': self.API_KEY
        }
        url = self.BASE_URL + "place/findplacefromtext/json"

        response = requests.get(
            url, 
            params = parameters
        )

        if response.status_code == 200:
            response_json = response.json()
        else:
            return None
        
        try:
            candidates = response_json["candidates"]
            location = candidates[0]["geometry"]["location"]
            lat = location["lat"]
            lng = location["lng"]
            return lat, lng
        except:
            return None

    def find_nearby_places(self, location):
        base_url = "https://maps.googleapis.com/maps/api/place/nearbysearch/json"
        amenities = []

        parameters = {
            'location': location,
            'radius': self.radius,
            'key': self.API_KEY
        }

        while True:  # This loop will continue to run as long as there's a next_page_token
            response = requests.get(
                base_url, 
                params = parameters
            )

            # Ensure the request was successful
            if response.status_code == 200:
                data = response.json()
                
                for result in data['results']:
                    types = self.types_to_include & set(result["types"])
                    latitude = result['geometry']['location']['lat']
                    longitude = result['geometry']['location']['lng']

                    for type in types:
                        amenity = Amenity(type, latitude, longitude)
                        amenities.append(amenity)

                # If there's a next_page_token, update the parameters to include it for the next request
                if 'next_page_token' in data:
                    parameters['pagetoken'] = data['next_page_token']
                    
                    # It's essential to wait a bit before the next request as the next_page_token might not be immediately valid
                    time.sleep(1)
                else:
                    break  # If there's no next_page_token, break out of the loop
            else:
                return None  # If the request wasn't successful, return None

        return amenities
    
    def distance(lat1, lng1, lat2, lng2):
        """
        Calculate the great circle distance between two points
        on the Earth (specified in decimal degrees).
        """
        # Convert decimal degrees to radians
        lat1, lng1, lat2, lng2 = map(math.radians, [lat1, lng1, lat2, lng2])

        # Haversine formula
        dlat = lat2 - lat1
        dlng = lng2 - lng1
        a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlng/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        r = 6371

        return c * r


