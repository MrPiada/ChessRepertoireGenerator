import requests
import chess.pgn
import chess
import json
import sys
import time
import pandas as pd

from chess.engine import Cp
from config import Config
from utils import *
from stats_plotter import *


class RepertoireBuilder:
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

        self.start_time = 0

        self.stats = pd.DataFrame(
            columns=[
                'ply',
                'move',
                'IsWhiteToMove',
                'whitePerc',
                'drawPerc',
                'blackPerc',
                'totGames',
                'percGames',
                'engineEval'])

        # TODO: creare una lista self.stats = [],
        #       la lista sarà riempita con un dizionario contenente
        #       la mossa (in formato san), score del bianco/patta/nero, ply, valutazione motore
        # TODO: sfruttare la lista stat per fare grafici in funzione del ply per vedere la qualità del repertorio
        # TODO: usare plotly in modo che ogni punto possa avere il tooltip che spiega la mossa
        # TODO: colorare di nero i punti delle mosse del nero e di bianco i
        # punti delle mosse del

    def GenerateReportoire(self):
        print("\n\t\tSTART\n")
        self.start_time = time.time()

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

        return self.stats

    def __make_move(self, move, node, move_comment):
        # eseguo la mossa richiesta
        child_node = node.add_variation(chess.Move.from_uci(move))

        elapsed_time = time.time() - self.start_time
        minutes, seconds = divmod(elapsed_time, 60)
        strTime = f"{minutes:.0f}m{seconds:.0f}s"

        board_header = f"\n({strTime}) ------- {child_node.ply()} {move} {move_comment}\n"
        board = str(child_node.board())
        clear_and_print(f"\n\n{board_header}\n{board}\n\n\n")

        move_hist = ply_hist(self.stats, max_depth=self.config.MaxDepth)
        white_perc_plot = plot_white_perc(
            self.stats, max_depth=self.config.MaxDepth)
        engine_eval_plot = plot_engine_eval(
            self.stats, max_depth=self.config.MaxDepth)

        plots = align_plots(
            white_perc_plot, engine_eval_plot, move_hist)
        print(plots)

        child_node.comment = move_comment
        eval = self.__get_cloud_eval(child_node.board().fen())

        if (eval != -9999):
            child_node.set_eval(chess.engine.PovScore(Cp(eval), chess.WHITE))

        # interrompo la ricerca se raggiungo la profondità massima
        if (child_node.ply() > self.config.MaxDepth):
            print("----- MAX DEPTH")
            return

        # ottengo il codice fen della posizione
        self.ApiDbParams["fen"] = child_node.board().fen()

        # eseguo la chiamata all'API lichess
        response = requests.get(self.ApiDbUrl, params=self.ApiDbParams)

        # parsing della response
        tree = json.loads(response.content.decode())

        candidate_moves = self.__GetCandidateMoves(child_node, tree)
        print("#CandidateMoves: ", len(candidate_moves))
        for move in candidate_moves:

            self.stats.loc[len(self.stats)] = [
                child_node.ply() + 1,
                move['san'],
                child_node.board().turn,
                move['white'],
                move['draws'],
                move['black'],
                move['tot_games'],
                move['perc'],
                move['eval']
            ]

            self.__make_move(
                move['uci'],
                child_node,
                move['comment'])

    def __get_cloud_eval(self, fen):
        self.ApiCloudEvalParams['fen'] = fen
        response = requests.get(
            self.ApiCloudEvalUrl,
            params=self.ApiCloudEvalParams)
        tree = json.loads(response.content.decode())
        # Se esiste la valutazione in cloud della mossa
        if ('pvs' in tree):
            if ('mate' in tree['pvs'][0]):
                return tree['pvs'][0]['mate'] * 1000
            return tree['pvs'][0]['cp']
        else:
            return -9999

    def __set_move_comment(self, move):
        if (move['eval'] != -99.99):
            comment = f"{move['perc']}% ({move['tot_games']}) -- {move['eval']} -- {move['white']}/{move['draws']}/{move['black']}"
        else:
            comment = f"{move['perc']}% ({move['tot_games']}) -- {move['white']}/{move['draws']}/{move['black']}"
        move['comment'] = comment

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
        # n = node.add_variation(chess.Move.from_uci(tree_move['uci']))

        # crea un nodo con la posizione iniziale
        board = node.board()
        new_board = board.copy()
        new_board.push(chess.Move.from_uci(tree_move['uci']))
        fen = new_board.fen()

        tree_move['eval'] = self.__get_cloud_eval(fen) / 100.

        self.__set_move_comment(tree_move)

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
                if (m['eval'] != -9999):
                    # scarto la mossa non è tra le prime tre del motore
                    if m["eval_pos"] > self.config.EngineLines:
                        continue
                    # scarto la mossa ha una valutazione del motore non accettabile (<
                    # -1 e tocca la bianco o > 1 e tocca al nero)
                    if (bIsWhiteToMove and m['eval'] < - self.config.EngineThreshold) or (
                            not bIsWhiteToMove and m['eval'] > self.config.EngineThreshold):
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
                if (perc_sum > self.config.FreqThreshold):
                    return ret_moves

        return ret_moves

    def __GetCandidateMoves(self, node, tree):
        total_games = tree['white'] + tree['draws'] + tree['black']

        if (len(tree['moves']) == 0):
            print("CandidateMoves --> no tree moves at the beginning")

        for move in tree['moves']:
            self.__compute_evaluations(node, move, total_games)

        # Rimuovo tutte le linee che non hanno valutazione cloud di lichess
        evalutad_moves = list(
            filter(
                lambda x: x['eval'] != -
                9999,
                tree['moves']))

        eval_sorted_moves = []
        if (len(evalutad_moves) == 0):
            print("CandidateMoves --> no evaluated moves, use all of them")
            evalutad_moves = tree['moves']
            eval_sorted_moves = sorted(evalutad_moves, key=lambda x: x["eval"])
        else:
            eval_sorted_moves = tree['moves']

        toMove_sorted_moves = []  # score relativo da db in base a chi deve muovere

        bIsWhiteToMove = node.board().turn
        if (bIsWhiteToMove):
            toMove_sorted_moves = sorted(
                evalutad_moves, key=lambda x: x["white"], reverse=True)
        else:
            toMove_sorted_moves = sorted(
                evalutad_moves, key=lambda x: x["black"], reverse=True)

        for i, item in enumerate(evalutad_moves):
            item["freq_pos"] = i
            item["eval_pos"] = eval_sorted_moves.index(item)
            item["dbscore_pos"] = toMove_sorted_moves.index(item)

        return self.__filter_moves(
            evalutad_moves,
            bIsWhiteToMove=bIsWhiteToMove,
            bIsWhiteRepertoire=self.bIsWhiteRepertoire)
