import warnings
import osmnx as ox
import pandas as pd
from shapely.geometry import Point, Polygon

class GeoService:
    
    def __init__(self, significant_places: dict[str : (int, int)], radius: int = 300):
        self.significant_places = significant_places
        self.radius = radius
        
    def initialize_osmnx_cache(self, cache_folder="ox_cache"):
        # Set up OSMnx to use a local cache folder
        ox.config(use_cache=True, cache_folder=cache_folder)
    
    def get_amenities_from_address(self, address: str):
        try:
            features = ox.features_from_address(
                address,
                tags = {"amenity" : True, "name:en" : True},
                dist = self.radius
            )
            
            features = features[["amenity", "name:en", "geometry"]]
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                features["geometry"] = features["geometry"].apply(self.__convert_coords)
                
            return features.dropna()
        except Exception as e:
            print(e)
            return None
    
    def get_amenities_from_point(self, coords: (int, int)):
        try:
            features = ox.features_from_point(
                coords,
                tags = {"amenity" : True},
                dist = self.radius
            )
            
            features = features[["amenity", "geometry"]]
            with warnings.catch_warnings():
                warnings.simplefilter('ignore', UserWarning)
                features["geometry"] = features["geometry"].apply(self.__convert_coords)
            
            return features.dropna()
        except:
            empty_df = pd.DataFrame(columns=['amenity', 'geometry'])
            return empty_df
        
    def __convert_coords(self, geom):
        if isinstance(geom, Point):
            coords = geom.coords.xy
            return (coords[1][0], coords[0][0])
        elif isinstance(geom, Polygon):
            return (geom.centroid.y, geom.centroid.x)
        
        return None
    
    def get_coord_from_address(self, address):
        # We are going to see the nearby amentities, 
        # and get the mean distance to the amentities
        amenities = self.get_amenities_from_address(address)
        if amenities is None:
            return None
        
        coords = amenities.geometry.to_list()
        c0 = [c[0] for c in coords]
        c1 = [c[1] for c in coords]
        count = len(c0)
        if count == 0:
            return (None, None)
        
        c0mean = sum(c0) / count
        c1mean = sum(c1) / count
        return (c0mean, c1mean)
    
    def distance_to_significant(self, coord):
        if coord is None:
            return None
        try:
            return {key : int(self.distance(value, coord)) for key, value in self.significant_places.items() }
        except Exception as e:
            print("RECEIVED NIL", coord, e, type(coord))
    
    def distance(self, coord1, coord2):
        """
        Calculate the great circle distance between two sets of coordinates using OSMnx.
        :param coord1: Tuple (lat1, lon1) representing the first point's coordinates
        :param coord2: Tuple (lat2, lon2) representing the second point's coordinates
        :return: Distance in kilometers
        """
        distance = ox.distance.great_circle(coord1[0], coord1[1], coord2[0], coord2[1])
        return distance

