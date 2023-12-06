import os
import pandas as pd
from PIL import Image
from torch.utils.data import Dataset, DataLoader
from torchvision import transforms
import torch

class ApartmentsDatasetPyTorch(Dataset):
    def __init__(self, device, dataframe, images_dir, transform=None):
        """
        Args:
            root_dir (string): Directory with all the images.
            transform (callable, optional): Optional transform to be applied
                on a sample.
        """
        
        self.images_dir = images_dir
        self.transform = transform
        self.image_paths = []
        self.df = dataframe
        self.device = device
        
        for subdir, dirs, files in os.walk(images_dir):
            for file in files:
                if file.endswith(".jpg") or file.endswith(".JPG") or file.endswith(".jpeg"):
                    img_path = os.path.join(subdir, file)
                    if os.path.getsize(img_path) > 0:
                        self.image_paths.append(img_path)
                    
        self.error_log = {}
        
    def tabular_data_size(self):
        return len(self.df.columns) - 3 # id, source, price
        
    def __len__(self):
        return len(self.image_paths)

    # Introducing is_valid, because sometimes there is a mismatch between 
    # the images and their tabular data. 
    def __getitem__(self, idx):
        image_path = self.image_paths[idx]
        components = image_path.split("/")
        source = components[-3]
        ap_native_id = components[-2]
        
        try:
            image = Image.open(image_path)
            if self.transform:
                image = self.transform(image)
            
        except Exception as e:
            self.error_log[idx] = f"Error loading image: {e}"
            raise Exception("IMAGE NOT FOUND")

        price = self.__get_price_from_image_path(image_path)
        if price is None:
            self.error_log[idx] = "Price not found"
            raise Exception("PRICE NOT FOUND", source, ap_native_id)

        image = image.to(self.device)

        # Optimize data operations
        data = self.df[(self.df["source"] == source) & (self.df["id"] == ap_native_id)]
        data = data.drop(columns=["id", "source", "price"]).values
        data_tensor = torch.as_tensor(data, dtype=torch.float32, device=self.device)  # Create tensor directly on the device

        return (image, data_tensor, price)

    def __get_price_from_image_path(self, image_path):
        components = image_path.split("/")
        source = components[-3]
        ap_native_id = components[-2]
        filtered_rows = self.df[(self.df["source"] == source) & (self.df["id"] == ap_native_id)]
        try:
            price = int(filtered_rows["price"])
        except:
            return None
        price_tensor = torch.tensor(price, dtype=torch.float32, device=self.device)  # Create tensor directly on the device
        return price_tensor

