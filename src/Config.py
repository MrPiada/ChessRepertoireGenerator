import yaml
from Utils import Color

class Config:
    def __init__(self, filename):
        with open(filename, 'r') as file:
            config_data = yaml.safe_load(file)
        
        # Lichess API call
        self.variant = config_data.get('variant', "standard")
        self.speeds = config_data.get('speeds', ["blitz","rapid","classical"])
        self.ratings = config_data.get('ratings', ["2200","2500"])
        
        # Pgn info
        self.PgnName = config_data.get('PgnName', "Repertoire.pgn")
        self.Event = config_data.get('Event', "ChessRepertoireGenerato")
        
        # Generator info
        self.Color = Color[((str)(config_data.get('Color', "White"))).upper()]
        self.StartingMove = config_data.get('WhiteStartingMove', "e2e4")
        self.MaxDepth = config_data.get('MaxDepth', 10)
        
        # Move filter info
        self.EngineLines = config_data.get('EngineLines', 3)  # se la mossa non è tra le prime tre del motore la scarto
        self.EngineThreshold = config_data.get('EngineThreshold', 1) # se la mossa ha una valutazione del motore non accettabile (< -1 e tocca la bianco o > 1 e tocca al nero) la scarto
        self.FreqThreshold = config_data.get('FreqThreshold', 80) # considero mosse fino al punto in cui ho coperto almeno l'80% delle mosse giocate
                
        self.boolean_field = config_data.get('boolean_field', False)
        self.numeric_field = config_data.get('numeric_field', 0)
