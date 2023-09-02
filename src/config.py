import yaml
import re

from enum import Enum
from utils import Color


class StartPositionType(Enum):
    STARTING_MOVE = 0
    MOVE_LIST = 1
    FEN = 2
    PGN = 3


class Config:
    def __init__(self, filename):
        with open(filename, 'r') as file:
            config_data = yaml.safe_load(file)

        # Lichess API call
        self.variant = config_data.get('variant', "standard")
        self.speeds = ",".join(
            config_data.get(
                'speeds', [
                    "blitz", "rapid", "classical"]))
        self.ratings = ",".join(
            str(r) for r in config_data.get(
                'ratings', [
                    "2200", "2500"]))

        # Pgn info
        self.PgnName = config_data.get('PgnName', "Repertoire.pgn")

        # Generator info
        self.Color = Color[((str)(config_data.get('Color', "White"))).upper()]

        self.MaxDepth = config_data.get('MaxDepth', 10)

        # Move filter info
        # se la mossa non è tra le prime tre del motore la scarto
        self.EngineLines = config_data.get('EngineLines', 3)
        # se la mossa ha una valutazione del motore non accettabile (< -1 e
        # tocca la bianco o > 1 e tocca al nero) la scarto
        self.EngineThreshold = config_data.get('EngineThreshold', 1)
        # considero mosse fino al punto in cui ho coperto almeno l'80% delle
        # mosse giocate
        self.FreqThreshold = config_data.get('FreqThreshold', 80)

        self.StartingPosition, self.StartingPositionType = self.__parse_starting_position(
            config_data.get('StartingPosition'))

        self.MinNumberOfGames = config_data.get('MinNumberOfGames', None)

    def __parse_starting_position(self, starting_position):
        starting_position_type = None

        fen_pattern = re.compile(
            r'^[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\/[rnbqkpRNBQKP1-8]+\s[wb]\s[KQkq-]+\s[a-h36-]\s\d+\s\d+$')

        if isinstance(
                starting_position, str) and bool(
                fen_pattern.match(starting_position)):
            starting_position_type = StartPositionType.FEN
        elif isinstance(starting_position, str) and starting_position.lower().endswith('.pgn'):
            starting_position_type = StartPositionType.PGN
        elif isinstance(starting_position, str):
            starting_position_type = StartPositionType.STARTING_MOVE
        elif isinstance(starting_position, list):
            starting_position_type = StartPositionType.MOVE_LIST

        return starting_position, starting_position_type
