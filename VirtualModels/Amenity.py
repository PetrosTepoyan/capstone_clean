class Amenity:
    def __init__(self, amenity_type, latitude, longitude):
        self.amenity_type = amenity_type
        self.latitude = latitude
        self.longitude = longitude

    def __repr__(self):
        return f"Amenity: {self.amenity_type}, Latitude: {self.latitude}, Longitude: {self.longitude}"
