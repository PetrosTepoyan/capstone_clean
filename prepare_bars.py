import json
import re
import ast
import pandas as pd
from utils.dummies import dummify_columns

def prepare_bars(
    raw_data_dir,
    location_converter,
    bars_building_type_mapping,
    bars_condition_mapping,
    bars_feature_mapping,
    common_features,
    skip_geo = False
    ):
    # Bars
    # Basic Cleaning
    print("Preparing Bars...")
    bars = pd.read_csv(raw_data_dir)
    bars = bars.dropna(axis = 1, how="all") # remove all NaN columns 
    bars['facilities'] = bars['facilities'].apply(ast.literal_eval)

    print("Basic cleaning...")
    new_buildings = (bars["building_type"] == "New building") & (bars["condition"] == "Without renovation")
    new_buildings = new_buildings.apply(lambda x: 1 if x else 0)
    bars["new_building"] = new_buildings

    bars["building_type"] = bars["building_type"]\
        .map(bars_building_type_mapping)\
        .fillna("Other")

    bars["condition"] = bars["condition"]\
        .map(bars_condition_mapping)\
        .fillna("Other")

    bars = bars.drop(columns = ["webpage", "ceiling_height"])

    print("Dummifying facilities...")
    # Dummifying Facilities
    f_feature_list = []
    for feature_list in bars["facilities"].to_list():
        feature_list = [bars_feature_mapping[feature] for feature in feature_list if feature in bars_feature_mapping]
        feature_list = [feature for feature in feature_list if feature in common_features]
        f_feature_list.append(feature_list)

    bars["facilities"] = f_feature_list
    bars = dummify_columns(bars, ["facilities"], common_features)

    # Bedrooms are not going to be used
    bars = bars.drop(columns = ["bedrooms"])
    bars = bars.dropna()

    if skip_geo == False:
        print("Formatting locations...")
        # Bars contains `location` as a physcial address
        bars["location"] = bars["location"]\
            .apply(lambda text: re.sub(r"\(.*?\)", "", text).strip())\
            .apply(lambda x: x.split("/")[-1])

        print("Converting address into coordinates...")
        bars["coordinates"] = bars["location"].apply(location_converter.convert)
    else:
        bars["coordinates"] = bars["location"]
    print("Done Bars")
    
    bars["latitude"] = bars["coordinates"].apply(lambda x: x[1])
    bars["longitude"] = bars["coordinates"].apply(lambda x: x[0])
    
    bars = bars.drop(columns = ["location", "coordinates"])
    
    print()
    return bars
