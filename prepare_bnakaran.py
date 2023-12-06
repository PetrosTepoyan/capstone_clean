import json
import re
import ast
import pandas as pd
from utils.dummies import dummify_columns

def prepare_bnakaran(
    raw_data_dir,
    location_converter,
    bnakaran_building_type_mapping,
    bnakaran_condition_mapping,
    bnakaran_feature_mapping,
    common_features,
    skip_geo = False
):
    # Bnakaran
    print("Preparing Bnakaran...")
    bnakaran = pd.read_csv(raw_data_dir)
    bnakaran = bnakaran.dropna(axis = 1, how="all") # remove all NaN columns 
    bnakaran['room_details'] = bnakaran['room_details'].apply(ast.literal_eval)
    bnakaran['additional_features'] = bnakaran['additional_features'].apply(ast.literal_eval)

    print("Basic cleaning...")
    bnakaran["new_building"] = bnakaran["webpage"].str\
        .contains("new-building")\
        .apply(lambda x: 1 if x else 0)

    bnakaran["building_type"] = bnakaran["construction_type"]\
        .map(bnakaran_building_type_mapping)\
        .fillna("Other")

    bnakaran["condition"] = bnakaran["renovation"]\
        .map(bnakaran_condition_mapping)\
        .fillna("Other")


    bnakaran = bnakaran.drop(columns = ["webpage", "renovation", "construction_type", "utilities"])

    bathroom_counts = []
    for details in bnakaran["room_details"]:
        bathroom_count = int(details.get("bathrooms", 0))
        bathroom_counts.append(bathroom_count)

    bnakaran = bnakaran.drop(columns = ["room_details"])
    bnakaran["bathroom_count"] = bathroom_counts

    print("Dummifying facilities...")
    f_feature_list = []
    for feature_list in bnakaran["additional_features"].to_list():
        feature_list = [bnakaran_feature_mapping[feature] for feature in feature_list if feature in bnakaran_feature_mapping]
        feature_list = [feature for feature in feature_list if feature in common_features]
        f_feature_list.append(feature_list)
    f_feature_list
    bnakaran["additional_features"] = f_feature_list
    bnakaran = dummify_columns(bnakaran, ["additional_features"], common_features)

    # Air Conditioner
    ac_present = bnakaran["cooling"].isna()
    ac_present = ac_present.apply(lambda x: 1 if x else 0)
    bnakaran["F_Air Conditioner"] = (ac_present + bnakaran["F_Air Conditioner"]).apply(lambda x: min(x, 1))

    # Heating
    heating_present = bnakaran["heating"].isna()
    heating_present = heating_present.apply(lambda x: 1 if x else 0)
    bnakaran["F_Heating System"] = (heating_present + bnakaran["F_Heating System"]).apply(lambda x: min(x, 1))
    bnakaran = bnakaran.drop(columns = ["cooling", "heating"])

    bnakaran = bnakaran.drop(columns = ["windows", "entrance_door", "parking",
                                        "flooring", "added_in_date", "visit_count"])
    print("Done Bnakaran")
    print()
    return bnakaran