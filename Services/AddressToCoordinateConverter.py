import ast
import pandas as pd
from fuzzywuzzy import fuzz

class AddressToCoordinateConverter:
    
    def __init__(self, streets_csv_path):
        self.streets = pd.read_csv(streets_csv_path)
    
    def convert(self, address):
        return self.get_top_matched_coordinate(df = self.streets, query = address)
    
    def get_top_matched_coordinate(self, df, query, debug = False):
        max_score = 0
        top_row = None

        for index, row in df.iterrows():
            score = fuzz.ratio(query.lower(), row['name_en'].lower())
            if score > max_score:
                max_score = score
                top_row = row

        if debug:
            return top_row
        else:
            # because it is a string when we read it from streets.csv
            return self.convert_to_tuple(top_row["coordinates"])
        
    def convert_to_tuple(self, cell):
        try:
            # Use ast.literal_eval to safely evaluate the string
            return ast.literal_eval(cell)
        except (ValueError, SyntaxError):
            # Handle the case where the cell is not a valid tuple string
            return None