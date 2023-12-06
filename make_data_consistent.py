import pandas as pd
import os
import shutil

def copy_images(from_dir, to_dir):
    shutil.copytree(from_dir, to_dir)

def delete_images_not_in_data(data_file, images_dir):
    # Load your dataset into a pandas DataFrame
    dataset = pd.read_csv(data_file)  # Change the file path accordingly
    # Define the directory path
    directory_path = images_dir  # Change to your actual directory path
    to_delete = []
    # Iterate through the folders in the directory
    for folder_name in os.listdir(images_dir):
        folder_path = os.path.join(images_dir, folder_name)

        # Check if the folder name (source) is in the dataset
        if folder_name in dataset['source'].values:
            folder_files = set(os.listdir(folder_path))

            # Extract the relevant IDs from the dataset for the current source
            ids_in_dataset = set(dataset[dataset['source'] == folder_name]['id'])

            # Calculate the set difference to find images not in the dataset
            files_to_delete = folder_files - ids_in_dataset

            # Delete the images not in the dataset
            for file_to_delete in files_to_delete:
                file_path = os.path.join(folder_path, file_to_delete)
                if "DS_Store" not in file_path:
                    to_delete.append(file_path)
        else:
            # If the source is not in the dataset, you can handle it accordingly
            print(f"Source '{folder_name}' not found in the dataset, skipping...")

    # If needed, you can add error handling for file operations
    print("Deleting", len(to_delete))
    for file_path in to_delete:
        shutil.rmtree(file_path)
        
def delete_datapoint_with_no_images(data_dir, images):

    # Load your dataset into a pandas DataFrame
    dataset = pd.read_csv(data_dir)  # Change the file path accordingly

    # Define the directory path
    directory_path = images  # Change to your actual directory path

    # Create a list to store indices of rows to delete
    rows_to_delete = []

    # Iterate through the DataFrame rows
    for index, row in dataset.iterrows():
        source = row['source']
        id_value = row['id']
        folder_path = os.path.join(directory_path, source)

        # Check if the image corresponding to the row exists in the directory
        if not os.path.exists(os.path.join(folder_path, id_value)):
            rows_to_delete.append(index)
    print(rows_to_delete)
    # Delete rows with no corresponding images
    dataset.drop(rows_to_delete, inplace=True)

    # If needed, reset the index of the modified DataFrame
    dataset.reset_index(drop=True, inplace=True)

    return dataset


import argparse
import matplotlib.pyplot as plt

parser = argparse.ArgumentParser(description="Matching arguments")
parser.add_argument('-data_dir', metavar='data_dir', type=str, help='Data directory')
parser.add_argument('-images_dir', metavar='data', type=str, help='Images directory')

args = parser.parse_args()
data_dir = args.data_dir
images_dir = args.images_dir

delete_images_not_in_data(
    data_dir,
    images_dir
)
dataset = delete_datapoint_with_no_images(
    data_dir,
    images_dir
)