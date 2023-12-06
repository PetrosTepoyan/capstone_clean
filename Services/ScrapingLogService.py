import pandas as pd
import threading

class ScrapingLogService:
    
    def __init__(self, path):
        self.path = path
        try:
            self.log_df = pd.read_csv(path, index_col=0)
        except:
            self.log_df = pd.DataFrame(columns=[
                "source",
                "webpage",
                "success",
                "error",
                "skipped"
            ])
        self.flash_interval = 0
        self.lock = threading.Lock()
        
    def did_scrape(self, webpage):
        with self.lock:
            # Check if the webpage exists in the log and if it was successfully scraped
            predicate = self.log_df['webpage'] == webpage
            same_webpage = self.log_df[predicate]
            if not same_webpage.empty:
                return True
            else:
                return False
        
    def start(self, source, webpage):
        
        new_row = pd.DataFrame({
            "source": [source],
            "webpage": [webpage],
            "success": [None],
            "error": [None],
            "skipped": [None]
        })
        
        with self.lock:
            self.log_df = pd.concat([self.log_df, new_row], ignore_index=True)
        
    def success(self, source, webpage):
        with self.lock:
            self.log_df.loc[(self.log_df['webpage'] == webpage), 'success'] = True
            self.__increment_and_save()
        
    def error(self, source, webpage, error):
        with self.lock:
            self.log_df.loc[(self.log_df['webpage'] == webpage), ['success', 'error']] = [False, error]
            self.__increment_and_save()

    def skipped(self, source, webpage):
        new_row = pd.DataFrame({
            "source": [source],
            "webpage": [webpage],
            "success": [None],
            "error": [None],
            "skipped": [True]
        })
        
        with self.lock:
            self.log_df = pd.concat([self.log_df, new_row], ignore_index=True)

    def __increment_and_save(self):
        self.flash_interval += 1
        if self.flash_interval > 0:
            self.flash_interval = 0
            self.save()
        
    def save(self):
        self.log_df.to_csv(self.path)
