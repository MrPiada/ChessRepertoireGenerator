import yaml

class Config:
    def __init__(self, filename):
        with open(filename, 'r') as file:
            config_data = yaml.safe_load(file)
        
        self.text_field = config_data.get('text_field')
        self.boolean_field = config_data.get('boolean_field', False)
        self.numeric_field = config_data.get('numeric_field', 0)
