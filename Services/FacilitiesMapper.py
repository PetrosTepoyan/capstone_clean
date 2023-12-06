# idea: use ChatGPT to map facilities into n different categories.

import json
import openai

class ApartmentFeatureMapper:
    
    def __init__(self, predefined_features: list[str]):
        self.predefined_features = predefined_features
        
        try:
            with open('config.json', 'r') as f:
                config = json.load(f)
            openai.api_key = config.get("OPENAI_API_KEY")
        except:
            print("Failed to initialize. Config file not found")
            
    
    def map(self, dirty_features: list[str]) -> list[str]:
        """
        dirty_features: list[str] - list of features from the website that need 
        to be engineered into a set of predefined features.
        """
        
        model = "gpt-3.5-turbo"
        messages = [{"role": "user", "content": "Hello world"}]
        
        completion = openai.ChatCompletion.create(
            model = model,
            messages = messages
        )
        print(completion.choices[0].message.content)
        