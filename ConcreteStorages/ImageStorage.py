import os
import pandas as pd
import threading

class ImageStorage:
    
    def __init__(self, images_path, image_error_log_path):
        self.images_path = images_path
        self.image_error_log_path = image_error_log_path
        self.flash_interval = 10
        self.lock = threading.Lock()
        self.image_error_log = pd.DataFrame(columns = [
            "source", "url", "apartment_id", "index", "error"
        ])
    
    def save_image(self, image, image_name):
        dir_path = os.path.dirname(self.images_path + image_name)
        if not os.path.exists(dir_path):
            os.makedirs(dir_path)

        with open(self.images_path + image_name, 'wb') as f:
            f.write(image)
            
    def log_error(self, source, url, apartment_id, index, error):
        print(error)
        new_row = pd.DataFrame({
            "source" : [source],
            "url" : [url],
            "apartment_id" : [apartment_id],
            "index" : [index],
            "error" : [error]
        })
        
        with self.lock:
            self.image_error_log = pd.concat([self.image_error_log, new_row])
            self.__increment_and_save()
            
    def __increment_and_save(self):
        self.flash_interval += 1
        if self.flash_interval > 3:
            self.__save_log()
        
    def __save_log(self):
        self.image_error_log.to_csv(self.image_error_log_path)