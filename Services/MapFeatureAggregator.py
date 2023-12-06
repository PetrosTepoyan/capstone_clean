import pandas as pd
from utils.ProgressBar import ProgressBar
from Services import GeoService

class MapFeatureAggregator:
    
    def __init__(self, geo_service: GeoService):
        self.geo_service = geo_service
    
    def significant_distances(self, data, location_col: str):
        all_distances = []
        locations = data[location_col]
        progress = ProgressBar(len(locations))
        for coordinate in locations:
            distances = self.geo_service.distance_to_significant(coordinate)
            all_distances.append(distances)
            progress.flush()
            
        df = pd.DataFrame(all_distances) 
        return df
    
    def amenities_count(self, data, location_col: str):
        aggregated_amentities_count = pd.DataFrame()
        locations = data[location_col]
        progress = ProgressBar(len(locations))
        for coordinate in locations:
            amenities_df = self.geo_service.get_amenities_from_point(coordinate)
            dict_to_add = amenities_df["amenity"].value_counts().to_dict()
            aggregated_amentities_count = self.add_row_from_dict_with_zeros(
                aggregated_amentities_count,
                dict_to_add
            )
            progress.flush()
        return aggregated_amentities_count
    
    def add_row_from_dict_with_zeros(self, df, data_dict):
        """
        Adds a row to the dataframe from a dictionary. New columns are added if they don't exist, 
        and are prepended with 'L' if they are new. Missing values are filled with 0.

        Args:
        df (pd.DataFrame): The dataframe to add the row to.
        data_dict (dict): The dictionary containing the data to add.

        Returns:
        pd.DataFrame: The updated dataframe.
        """
        # Prepend 'L' to new columns
        new_columns = {key: 'L_' + key if key not in df.columns else key for key in data_dict.keys()}
        updated_dict = {new_columns[key]: value for key, value in data_dict.items()}

        # Add missing columns to the dataframe with 0 values
        for col in new_columns.values():
            if col not in df.columns:
                df[col] = 0

        # Replace NaN in the dictionary with 0 for existing columns
        for col in df.columns:
            if col not in updated_dict:
                updated_dict[col] = 0

        # Add the new row
        new_row = pd.DataFrame([updated_dict], columns=df.columns)
        df = pd.concat([df, new_row], ignore_index=True)

        return df