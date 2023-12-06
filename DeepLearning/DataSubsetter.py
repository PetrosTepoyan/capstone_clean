import pandas as pd

class DataSubsetter:
    
    def __init__(self, data_dir):
        self.data = pd.read_csv(data_dir)
        
    def without_group(self, group_prefix, data_provided = None):
        if data_provided is not None:
            return data_provided[[col for col in data_provided.columns if group_prefix not in col]]
        else:
            return self.data[[col for col in self.data.columns if group_prefix not in col]]
    
    def without_groups(self, group_prefixes: list, data_provided = None):
        if data_provided is not None:
            data = data_provided
        else:
            data = self.data
            
        for p in group_prefixes:
            data = self.without_group(p, data_provided = data)
        return data
    
    def without_cols(self, cols, data_provided = None):
        if data_provided is not None:
            return data_provided[[col for col in data_provided.columns if col not in cols]]
        else:
            return self.data[[col for col in self.data.columns if col not in cols]]
    
    def without(self, groups = None, cols = None):
        data = self.data
        if cols:
            data = self.without_cols(cols, data_provided = data)
            
        if groups:
            if isinstance(groups, list):
                data = self.without_groups(groups, data_provided = data)
            else:
                data = self.without_group(groups, data_provided = data)
        return data