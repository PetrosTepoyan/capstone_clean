import os
import csv
from Protocols.Storage import Storage
import threading
import logging

class CSVStorage(Storage):
    fieldnames = [
        "source", 
        "webpage",
        "id",
        "price", 
        "facilities", "location", "area", 
        "rooms", "floor", "storeys", 
        "building_type", 'condition', 
        'ceiling_height', 'bathroom_count',
        'bedrooms', 'added_in_date', "view_count",
        'additional_features', 'latitude', 
        'visit_count', 'utilities', 'room_details', 
        'details', 'longitude', 'flooring', 'entrance_door', 'construction_type', 
        'renovation', 'windows', 'heating', 'parking', 'cooling']

    # Flush each 5 datapoints
    flush_batch_count: int = 1

    def __init__(self, file_path):
        self.file_path = file_path
        self.file_handle = None
        self.threadLock = threading.Lock()
        self.current_count = 0

    def initialize(self):
        # Check if the directory exists, and if not, create it
        directory = os.path.dirname(self.file_path)
        if not os.path.exists(directory):
            print(f"Creating the directory: {directory}")
            try:
                os.makedirs(directory)
            except Exception as e:
                print(f"Error creating the directory: {e}")
                return

        # Now, check if the file exists, and if not, create it
        if not os.path.exists(self.file_path):
            print(f"Creating the file: {self.file_path}")
            try:
                with open(self.file_path, mode='w', newline='') as file:
                    writer = csv.DictWriter(file, fieldnames=self.fieldnames)
                    writer.writeheader()
            except Exception as e:
                print(f"Error creating the file: {e}")
                return
        # Open the file for writing and store the file handle
        self.file_handle = open(self.file_path, mode='a+', newline='')

    def close_file(self):
        # Close the file when done
        if self.file_handle is not None:
            self.file_handle.close()

    def append(self, data_dict):
        # Append data in the CSV file
        if self.file_handle is not None:
            writer = csv.DictWriter(self.file_handle, fieldnames=self.fieldnames)
            # self.threadLock.acquire()
            writer.writerow(data_dict)
            self.current_count += 1
            if self.current_count == self.flush_batch_count:
                self.current_count = 0
                self.file_handle.flush()  # Flush to write data immediately
            # self.threadLock.release()

    def path(self):
        return self.file_path