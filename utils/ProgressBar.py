from IPython.display import clear_output

class ProgressBar:
    
    def __init__(self, total_count: int):
        self.total_count = total_count
        self.current_count = 0
        
    def flush(self, info = None):
        clear_output(wait=True)
        self.current_count += 1
        if info:
            print(f"Progress: {self.current_count}/{self.total_count} | {info}")
        else:
            print(f"Progress: {self.current_count}/{self.total_count}")