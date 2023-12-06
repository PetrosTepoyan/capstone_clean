import json
import re
import ast
import pandas as pd
from utils.dummies import dummify_columns
from utils.formatting import myrealty_format_address

def prepare_myrealty(
    raw_data_dir,
    location_converter,
    myrealty_building_type_mapping,
    myrealty_condition_mapping,
    myrealty_feature_mapping,
    common_features,
    skip_geo = False
):
    print("Preparing MyRealty...")
    myrealty = pd.read_csv(raw_data_dir)
    myrealty = myrealty.dropna(axis = 1, how="all") # remove all NaN columns 

    print("Basic cleaning...")
    myrealty["new_building"] = myrealty["webpage"].str\
        .contains("new-construction")\
        .apply(lambda x: 1 if x else 0)

    myrealty["bathroom_count"] = myrealty["bathroom_count"]\
        .replace(to_replace=r'\D', value='', regex=True)\
        .astype(int)

    # Condition
    myrealty["condition"] = myrealty["condition"].map(myrealty_condition_mapping)

    myrealty['facilities'] = myrealty['facilities'].apply(ast.literal_eval)

    myrealty = myrealty.drop(columns = [
        "webpage",
        "view_count",
        "added_in_date",
        "ceiling_height"
    ])

    print("Dummifying facilities...")
    f_feature_list = []
    for feature_list in myrealty["facilities"].to_list():
        feature_list = [myrealty_feature_mapping[feature] for feature in feature_list if feature in myrealty_feature_mapping]
        feature_list = [feature for feature in feature_list if feature in common_features]
        f_feature_list.append(feature_list)
        
    myrealty["facilities"] = f_feature_list
    myrealty = dummify_columns(myrealty, ["facilities"], common_features)

    print("Converting address into coordinates...")
    myrealty['location'] = myrealty['location'].apply(myrealty_format_address)
    if skip_geo == False:
        myrealty["coordinates"] = myrealty["location"].apply(location_converter.convert)
    else:
        myrealty["coordinates"] = myrealty["location"]
        
    myrealty["latitude"] = myrealty["coordinates"].apply(lambda x: x[1])
    myrealty["longitude"] = myrealty["coordinates"].apply(lambda x: x[0])
    myrealty = myrealty.drop(columns = ["coordinates", "location"])
    
    print("Done MyRealty")
    return myrealty