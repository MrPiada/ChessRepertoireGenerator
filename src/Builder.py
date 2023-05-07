from Config import Config

class MyClass:
    def __init__(self, config):
        self.config = config
        
        self.ApiDbUrl = "https://explorer.lichess.ovh/lichess"
        self.ApiDbParams = {
            "variant": self.config.variant,
            "speeds": self.config.speeds, 
            "ratings": self.config.ratings,
            "fen": None
            }
        
        self.ApiCloudEvalUrl = url_eval = "https://lichess.org/api/cloud-eval"
        self.ApiCloudEvalParams = {
            "variant": self.config.variant,
            "multiPv": "1", 
            "fen": None 
            }
    
    def compute(self):
        # Implementazione della funzione compute qui
        pass
