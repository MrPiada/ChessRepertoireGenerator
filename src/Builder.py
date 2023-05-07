import requests
import chess.pgn
import chess
import json

from chess.engine import Cp
from Config import Config
from Utils import Color


class MyClass:
    def __init__(self, config):
        self.config = config
        self.bIsWhiteRepertoire = (self.config.Color == Color.WHITE)
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
        self.__make_move(self.config.StartingMove, game, "Starting move")

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
        if (child_node.ply() > self.config.MaxDepth):
            return

        # ottengo il codice fen della posizione
        self.ApiDbParams["fen"] = child_node.board().fen()

        # eseguo la chiamata all'API lichess
        response = requests.get(self.ApiDbUrl, params=self.ApiDbParams)

        # parsing della response
        tree = json.loads(response.content.decode())

        # comment = self.__get_comment(tree)

        for move in self.__GetCandidateMoves(child_node, tree):
            self.__make_move(
                tree['moves'][0]['uci'],
                child_node,
                "",
                self.config.MaxDepth)

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
        tot = w + b + d
        perc_w = (int)(w / tot * 100)
        perc_b = (int)(b / tot * 100)
        perc_d = (int)(d / tot * 100)
        comment = f"{perc_w}/{perc_d}/{perc_b}"
        return comment

    def __compute_evaluations(self, node, tree_move, total_games):
        w = tree_move['white']
        b = tree_move['black']
        d = tree_move['draws']
        tot = w + b + d
        tree_move['tot_games'] = tot
        tree_move['white'] = (int)(w / tot * 100)
        tree_move['black'] = (int)(b / tot * 100)
        tree_move['draws'] = (int)(d / tot * 100)
        tree_move['strongest_practical'] = tree_move['white'] if (
            node.board().turn) else tree_move['black']
        tree_move['perc'] = (int)((float)(tot) / total_games * 100.)
        n = node.add_variation(chess.Move.from_uci(tree_move['uci']))
        tree_move['eval'] = self.__get_cloud_eval(n) / 100.

    def __filter_moves(self, move_list, bIsWhiteToMove, bIsWhiteRepertoire):
        """filtra le mosse per trovare o le candidate per il giocatore oppure quelle da considerare dagli avversari

        Args:
            move_list (list): tree['moves']
            bIsWhiteToMove (bool): deve muovere il bianco ?
            bIsWhiteRepertoire (bool): booleano che indica se si sta costruendo un repertorio per il bianco o per il nero

        Returns:
            list: lista delle mosse candidate e loro relativi commenti
        """

        ret_moves = []

        bIsPlayerTurn = (bIsWhiteToMove == bIsWhiteRepertoire)

        if (bIsPlayerTurn):
            sorted_moves = sorted(
                move_list,
                key=lambda x: x["strongest_practical"],
                reverse=True)

            for m in sorted_moves:
                if m["eval_pos"] > 3:  # se la mossa non è tra le prime tre del motore la scarto
                    continue
                # se la mossa ha una valutazione del motore non accettabile (<
                # -1 e tocca la bianco o > 1 e tocca al nero) la scarto
                if (bIsWhiteToMove and m['eval'] < -
                        1) or (not bIsWhiteToMove and m['eval'] > 1):
                    continue
                ret_moves.append(m)
                return ret_moves  # se tocca al giocatore considero solo una mossa alla volta
        else:
            sorted_moves = sorted(
                move_list,
                key=lambda x: x["perc"],
                reverse=True)
            perc_sum = 0
            for m in sorted_moves:
                ret_moves.append(m)
                perc_sum += m["perc"]
                # considero mosse fino al punto in cui ho coperto almeno l'80%
                # delle mosse giocate
                if (perc_sum > 80):
                    return ret_moves

        return ret_moves

    def __GetCandidateMoves(self, node, tree):
        total_games = tree['white'] + tree['draws'] + tree['black']
        for move in tree['moves']:
            self.__compute_evaluations(node, move, total_games)

        eval_sorted_moves = sorted(tree['moves'], key=lambda x: x["eval"])

        toMove_sorted_moves = []  # score relativo da db in base a chi deve muovere

        bIsWhiteToMove = node.board().turn
        if (bIsWhiteToMove):
            toMove_sorted_moves = sorted(
                tree['moves'], key=lambda x: x["white"], reverse=True)
        else:
            toMove_sorted_moves = sorted(
                tree['moves'], key=lambda x: x["black"], reverse=True)

        for i, item in enumerate(tree['moves']):
            item["freq_pos"] = i
            item["eval_pos"] = eval_sorted_moves.index(item)
            item["dbscore_pos"] = toMove_sorted_moves.index(item)

        return self.__filter_moves(
            tree['moves'],
            bIsWhiteToMove=bIsWhiteToMove,
            bIsWhiteRepertoire=self.bIsWhiteRepertoire)
