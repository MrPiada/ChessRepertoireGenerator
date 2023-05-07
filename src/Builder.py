import requests
import chess.pgn
import chess
import json

from chess.engine import Cp
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
    
    def GenerateReportoire(self):
        
        print("Create pgn game")
        game = chess.pgn.Game()
        game.headers["Event"] = self.config.Event
        
        # TODO: va poi deciso come iniziare un repertorio per il nero 
        #       --> gli si fa creare un repertorio partendo dalle varie mosse del bianco ???
        self.__make_move("e2e4", game, "", 2)
        
        # Salvataggio della partita in formato PGN
        with open(self.config.PgnName, "w") as f:
            exporter = chess.pgn.FileExporter(f)
            game.accept(exporter)
        
        pass
    
    
    def __make_move(self, move, node, move_comment):
        # eseguo la mossa richiesta
        child_node = node.add_variation(chess.Move.from_uci(move))
        child_node.comment = move_comment        
        eval = self.__get_cloud_eval(child_node)
        
        child_node.set_eval(chess.engine.PovScore(Cp(42), chess.WHITE))
        
        # interrompo la ricerca se raggiungo la profondità massima
        if(child_node.ply() > self.config.MaxDepth):
            return
        
        # ottengo il codice fen della posizione
        self.ApiDbParams["fen"] = child_node.board().fen()
        
        # eseguo la chiamata all'API lichess
        response = requests.get(self.ApiDbUrl, params=self.ApiDbParams)
        
        # parsing della response
        tree = json.loads(response.content.decode())
        
        comment = self.__get_comment(tree)
        
        # Chiamata ricorsiva
        self.__make_move(tree['moves'][0]['uci'], child_node, comment, self.config.MaxDepth)
        self.__make_move(tree['moves'][1]['uci'], child_node, comment, self.config.MaxDepth)
        
        
    def __get_cloud_eval(self, node):
        self.ApiCloudEvalParams['fen'] = node.board().fen()
        response = requests.get(self.ApiCloudEvalUrl, params=params_eval)
        tree = json.loads(response.content.decode())
        return tree['pvs'][0]['cp']
    
    
    def __get_comment(self, tree):
        # Commento dello score
        w = tree['white']
        b = tree['black']
        d = tree['draws']
        tot = w+b+d
        perc_w = (int)(w/tot * 100)
        perc_b = (int)(b/tot * 100)
        perc_d = (int)(d/tot * 100)
        comment = f"{perc_w}/{perc_d}/{perc_b}"
        return comment
