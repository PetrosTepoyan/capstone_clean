
import json 
import pandas as pd
import warnings
import ast
import numpy as np
from scipy import stats
import argparse

# Services
from Services import GeoService, MapFeatureAggregator, AddressToCoordinateConverter

parser = argparse.ArgumentParser(description='Process the script arguments')
parser.add_argument('-data_dir', type=str, help='Directory where the CSV files will be saved')

# Parse the arguments
args = parser.parse_args()
data_dir = args.data_dir

with open("config.json", 'r') as file:
    config = json.load(file)
    building_type_mapping = config["building_type_mapping"]
    for key in building_type_mapping:
        building_type_mapping[key][None] = "Other"
        
    commong_features = set(config["COMMON_FEATURES"])
    feature_mapping = config["feature_mapping"]
    condition_mapping = config["condition_type_mapping"]
    significant_places = config["significant_places"]
    important_amenities = config["important_amenities"]
    
converter = AddressToCoordinateConverter("utils/streets.csv")
geo_service = GeoService(
    {"SL_" + k : ast.literal_eval(v) for (k, v) in significant_places.items()},
    radius = 300
)
aggregator = MapFeatureAggregator(geo_service)

from prepare_bars import prepare_bars
from prepare_myrealty import prepare_myrealty
from prepare_bnakaran import prepare_bnakaran

def combine_datas(bars, myrealty, bnakaran):

    print("Combining data together")
    data = pd.concat([
        bars,
        myrealty,
        bnakaran
    ], axis = 0)
    data = data.reset_index(drop = True)

    # Removing webpages where `rent` is in the webpage
    scraping_log = pd.read_csv(data_dirs["scraping_log"], index_col=0)
    rents = scraping_log[scraping_log.webpage.str.contains("rent")]
    rents = rents[rents.success == True]
    bnakaran_raw = pd.read_csv(data_dirs["bnakaran"], index_col=0)
    myrealty_raw = pd.read_csv(data_dirs["myrealty"], index_col=0)
    
    renting_ap = bnakaran_raw[bnakaran_raw.webpage.isin(rents.webpage)]
    filtered_data_bnakaran = data[(data["source"] == 'bnakaran') & (data["id"].isin(renting_ap["id"]))]
    data = data.drop(filtered_data_bnakaran.index)

    renting_ap = myrealty_raw[myrealty_raw.webpage.isin(rents.webpage)]
    renting_ap_ids = renting_ap['id'].astype(str)

    filtered_data_myrealty = data[(data["source"] == 'myrealty') & (data["id"].isin(renting_ap_ids))]
    data = data.drop(filtered_data_myrealty.index)
    
    # Removing webpages where `vacation` is in the webpage
    vacation_bnakaran = bnakaran_raw[bnakaran_raw.webpage.str.contains("vacation")]
    vacation_rows_to_delete = data[(data["source"] == 'bnakaran') & (data["id"].isin(vacation_bnakaran["id"]))]
    data = data.drop(vacation_rows_to_delete.index)
    data = data.reset_index(drop = True)
    
    print("Total deleted", len(vacation_rows_to_delete) + len(filtered_data_bnakaran) + len(filtered_data_myrealty))
    print("Rows after deletion", data.shape)
    print()
    print("Preparing to aggregate with map features...")
    
    data["coordinates"] = data.apply(lambda row: (row['longitude'], row['latitude']), axis=1)
    
    data.to_csv(f"{data_dir}/data_nomap_badprice.csv", index = False)
    
    print("Adding significant locations...")
    significant_distances = aggregator.significant_distances(data, "coordinates")
    significant_distances = significant_distances.reset_index(drop = True)
    significant_distances.to_csv(f"{data_dir}/significant_locations.csv", index=False)
    
    print("Adding amenities...")
    amenities = aggregator.amenities_count(data, "coordinates")
    
    data = pd.concat([
        data,
        significant_distances,
        amenities[important_amenities]
    ], axis = 1)
    
    # Removing outliers
    Q1 = data[['price', 'area']].quantile(0.25)
    Q3 = data[['price', 'area']].quantile(0.75)
    IQR = Q3 - Q1
    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR
    outliers = ((data[['price', 'area']] < lower_bound) | (data[['price', 'area']] > upper_bound)).any(axis=1)
    outliers_count = outliers.sum()
    data = data[~outliers]
    
    data = data[data.price > 1000] # removing obvious outliers
    
    # Processing the price
    data.loc[data.price < 20000, 'price'] = data[data.price < 20000].price * data[data.price < 20000].area
    data = data.drop(columns = ["coordinates"])
    
    data = pd.get_dummies(data, columns = ["building_type", "condition"])
    data.drop(columns = ["building_type_Other", "condition_Other"])
    data = data.drop_duplicates(["source", "id"])
    
    data = data.dropna()
    return data

data_dirs = {
    "bars" : "scraping_results/data/bars_apartments.csv",
    "myrealty" : "scraping_results/data/myrealty_apartments.csv",
    "bnakaran" : "scraping_results/data/bnakaran_apartments.csv",
    "scraping_log" : "scraping_results/scraping_log.csv"
}

bars = prepare_bars(
    data_dirs["bars"],
    location_converter = converter,
    bars_building_type_mapping = building_type_mapping["bars"],
    bars_condition_mapping = condition_mapping["bars"],
    bars_feature_mapping = feature_mapping["bars"],
    common_features = commong_features,
    skip_geo = False
)
print()

myrealty = prepare_myrealty(
    data_dirs["myrealty"],
    location_converter = converter,
    myrealty_building_type_mapping = None,
    myrealty_condition_mapping = condition_mapping["myrealty"],
    myrealty_feature_mapping = feature_mapping["myrealty"],
    common_features = commong_features,
    skip_geo = False
)
print()

bnakaran = prepare_bnakaran(
    data_dirs["bnakaran"],
    location_converter = converter,
    bnakaran_building_type_mapping = building_type_mapping["bnakaran"],
    bnakaran_condition_mapping = condition_mapping["bnakaran"],
    bnakaran_feature_mapping = feature_mapping["bnakaran"],
    common_features = commong_features,
    skip_geo = False
)
print()

bars.to_csv(f"{data_dir}/bars_almost_ready.csv", index=False)
myrealty.to_csv(f"{data_dir}/myrealty_almost_ready.csv", index=False)
bnakaran.to_csv(f"{data_dir}/bnakaran_almost_ready.csv",index=False)

data = combine_datas(
    bars,
    myrealty,
    bnakaran
)


data.to_csv(f"{data_dir}/data.csv",index=False)
data_small = data.sample(frac=1).reset_index(drop=True)[:300]
data_small.to_csv(f"{data_dir}/data_small.csv", index=False)
data_small[:100].to_csv(f"{data_dir}/data_tiny.csv", index=False)
print("Done")