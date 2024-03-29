import json
import signal
import time
import requests
import chess.pgn
import chess
import pandas as pd

from chess.engine import Cp
from config import StartPositionType
from utils import Color, align_printables, clear_and_print, format_move_infos, is_uci_move, get_stylish_chessboard
from stats_plotter import ply_hist, plot_white_perc, plot_engine_eval, plot_open_moves
from tabulate import tabulate
from logger import Logger
from report import Report

GRACEFULL_EXIT = False
OPEN_MOVES = 0
UI_UPDATES = 0


class RepertoireBuilder:
    def __init__(self, config, options):
        # Register the signal handler for SIGINT (Ctrl+C)
        signal.signal(signal.SIGINT, self.__graceful_exit)

        self.config = config
        self.is_white_repertoire = self.config.Color == Color.WHITE
        self.api_db_url = "https://explorer.lichess.ovh/lichess"
        self.api_db_params = {
            "variant": self.config.variant,
            "speeds": self.config.speeds,
            "ratings": self.config.ratings,
            "fen": None
        }

        self.api_cloud_eval_url = "https://lichess.org/api/cloud-eval"
        self.api_cloud_eval_params = {
            "variant": self.config.variant,
            "multiPv": "1",
            "fen": None
        }

        self.starting_position = self.config.StartingPosition
        self.starting_position_type = self.config.StartingPositionType
        self.min_games = self.config.MinNumberOfGames

        self.start_time = 0

        logfile_name = self.config.PgnName
        self.logger = Logger(logfile_name)

        self.options = options

        self.session = requests.Session()

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

        self.open_moves = []
        self.ui_updates = []
        self.leaves = []
        self.nodes_fen = []

    def __graceful_exit(self, *args):
        """Handler for Ctrl+C (SIGINT) signal."""
        global GRACEFULL_EXIT
        GRACEFULL_EXIT = True

        self.logger.warning("Gracefully exiting...")

    def GenerateReportoire(self):

        self.logger.info("START GenerateReportoire()")

        self.start_time = time.time()

        game, node = self.__setup_initial_position(
            self.starting_position, self.starting_position_type)

        try:
            self.__make_move(
                "",
                node,
                "Starting move",
                None,
                starting_move=True)
        except KeyboardInterrupt:
            self.__graceful_exit()

        self.logger.info("END GenerateReportoire()")

        output_repertoire_file = self.config.PgnName + '.pgn'
        # Salvataggio della partita in formato PGN
        with open(output_repertoire_file, "w") as f:
            exporter = chess.pgn.FileExporter(f)
            game.accept(exporter)

        leaves_table = tabulate(self.leaves, headers="keys", tablefmt="grid")
        leaves = "LEAVES\n" + leaves_table
        self.logger.debug(leaves)

        report = Report(self.config, self.leaves, self.stats)
        report.evaluate_repertoire()

    def __setup_initial_position(
            self,
            starting_position,
            starting_position_type):
        game = chess.pgn.Game()
        node = game

        self.logger.info(
            f"position: {starting_position}\t type: {starting_position_type}")

        try:
            if starting_position_type == StartPositionType.STARTING_MOVE:
                if is_uci_move(starting_position):
                    node = node.add_variation(
                        chess.Move.from_uci(starting_position))
                else:
                    node = node.add_variation(
                        node.board().push_san(starting_position))

            elif starting_position_type == StartPositionType.MOVE_LIST:
                for move in starting_position:
                    if is_uci_move(move):
                        node = node.add_variation(
                            chess.Move.from_uci(move))
                    else:
                        node = node.add_variation(
                            node.board().push_san(move))

            elif starting_position_type == StartPositionType.FEN:
                node.setup(starting_position)

            elif starting_position_type == StartPositionType.PGN:
                with open(starting_position, 'r') as pgn_file:
                    pgn_game = chess.pgn.read_game(pgn_file)
                    board = pgn_game.board()
                    for move in pgn_game.mainline_moves():
                        board.push(move)
                    node.setup(board.fen())

        except Exception as e:
            self.logger.error(
                f"An error occurred while initializing the game: {e}")
            game = None

        return game, node

    def __make_move(
            self,
            move,
            node,
            move_san,
            move_comment,
            full_move_info=None,
            starting_move=False):
        global OPEN_MOVES
        global GRACEFULL_EXIT
        if GRACEFULL_EXIT:
            return

        if starting_move:
            child_node = node
        else:
            # eseguo la mossa richiesta
            child_node = node.add_variation(chess.Move.from_uci(move))

        self.logger.info(
            f"__make_move(move:{move}, node:{node}, move_san:{move_san}, full_move_info:{full_move_info}, starting_move:{starting_move})")
        self.__update_UI(child_node, move_san, full_move_info)

        self.nodes_fen.append(child_node.board().fen())

        if move_comment is not None:
            child_node.comment = move_comment

        engine_eval = self.__get_cloud_eval(child_node.board().fen())
        if engine_eval != -9999:
            child_node.set_eval(
                chess.engine.PovScore(
                    Cp(engine_eval),
                    chess.WHITE))


        # ottengo il codice fen della posizione
        self.api_db_params["fen"] = child_node.board().fen()

        # eseguo la chiamata all'API lichess
        response = self.__ask_lichess_api(
            self.api_db_url, self.api_db_params)

        # parsing della response
        tree = json.loads(response.content.decode())

        candidate_moves = self.__get_candidate_moves(child_node, tree)
        self.logger.info(f"#CandidateMoves: {len(candidate_moves)}")
        self.logger.debug(candidate_moves)
        
        # interrompo la ricerca se raggiungo la profondità massima
        if child_node.ply() > self.config.MaxDepth and len(candidate_moves) > 1:
            full_move_info['fen'] = child_node.board().fen()
            self.leaves.append(full_move_info)
            self.logger.info("----- MAX DEPTH")
            return
        
        if child_node.ply() > self.config.MaxDepth and len(candidate_moves) == 1:
            self.logger.info("Only one candidates: keep going even if max deptht")
            
        if len(candidate_moves) == 0:
            self.logger.info("No candidates moves")

        OPEN_MOVES += len(candidate_moves)

        for m in candidate_moves:

            if self.__check_for_transposition(m['san'], child_node):
                self.logger.debug(
                    f"transposition: move {m['san']} already analyzed")

            if m['tot_games'] < self.min_games:
                self.logger.debug(
                    f"not enough games ({m['tot_games']}) for move {m['san']}")

            self.stats.loc[len(self.stats)] = [
                child_node.ply() + 1,
                m['san'],
                child_node.board().turn,
                m['white'],
                m['draws'],
                m['black'],
                m['tot_games'],
                m['perc'],
                m['eval']
            ]

            self.__make_move(
                m['uci'],
                child_node,
                m['san'],
                m['comment'],
                m)

        OPEN_MOVES -= len(candidate_moves)

    def __get_cloud_eval(self, fen):
        self.api_cloud_eval_params['fen'] = fen
        response = self.__ask_lichess_api(
            self.api_cloud_eval_url,
            self.api_cloud_eval_params)

        tree = json.loads(response.content.decode())
        # Se esiste la valutazione in cloud della mossa
        if 'pvs' in tree:
            if 'mate' in tree['pvs'][0]:
                return tree['pvs'][0]['mate'] * 1000
            return tree['pvs'][0]['cp']

        return -9999

    def __set_move_comment(self, move, is_player_turn):
        move['comment'] = None

        comment = None

        if is_player_turn:
            rare_move = move['perc'] < 10
            excellent_score = move['strongest_practical'] > 70
            if rare_move or excellent_score:
                comment = ""
            if rare_move and excellent_score:
                comment += "!"
            if rare_move:
                comment += f"\nrare move ({move['perc']}%)"
            if excellent_score:
                comment += f"\nexcellent score ({move['strongest_practical']})"

        if not is_player_turn:
            common_move = move['perc'] > 50
            bad_score = move['strongest_practical'] < 30
            if common_move or bad_score:
                comment = ""
            if common_move and bad_score:
                comment += "?"
            if common_move:
                comment += f"\ncommon move ({move['perc']}%)"
            if bad_score:
                comment += f"\nbad score ({move['strongest_practical']})"

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

    def __filter_moves(self, move_list, is_white_to_move, is_white_repertoire):
        """filtra le mosse per trovare o le candidate per il giocatore oppure quelle da considerare dagli avversari

        Args:
            move_list (list): tree['moves']
            is_white_to_move (bool): deve muovere il bianco ?
            is_white_repertoire (bool): booleano che indica se si sta costruendo un repertorio per il bianco o per il nero

        Returns:
            list: lista delle mosse candidate e loro relativi commenti
        """

        ret_moves = []

        is_player_turn = is_white_to_move == is_white_repertoire

        if is_player_turn:
            sorted_moves = sorted(
                move_list,
                key=lambda x: x["strongest_practical"],
                reverse=True)

            for m in sorted_moves:
                if m['eval'] != -9999:
                    # scarto la mossa non è tra le prime tre del motore
                    if m["eval_pos"] > self.config.EngineLines:
                        self.__set_move_comment(m, is_player_turn)
                        continue
                    # scarto la mossa ha una valutazione del motore non accettabile (<
                    # -1 e tocca la bianco o > 1 e tocca al nero)
                    if (is_white_to_move and m['eval'] < - self.config.EngineThreshold) or (
                            not is_white_to_move and m['eval'] > self.config.EngineThreshold):
                        self.__set_move_comment(m, is_player_turn)
                        continue
                self.__set_move_comment(m, is_player_turn)
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
                self.__set_move_comment(m, is_player_turn)
                if perc_sum > self.config.FreqThreshold:
                    return ret_moves

        return ret_moves

    def __get_candidate_moves(self, node, tree):
        total_games = tree['white'] + tree['draws'] + tree['black']

        if len(tree['moves']) == 0:
            self.logger.info(
                "CandidateMoves --> no tree moves at the beginning")

        for move in tree['moves']:
            self.__compute_evaluations(node, move, total_games)

        # Rimuovo tutte le linee che non hanno valutazione cloud di lichess
        evalutad_moves = list(
            filter(
                lambda x: x['eval'] != -
                9999,
                tree['moves']))

        eval_sorted_moves = []
        if len(evalutad_moves) == 0:
            self.logger.info(
                "CandidateMoves --> no evaluated moves, use all of them")
            evalutad_moves = tree['moves']
            eval_sorted_moves = sorted(evalutad_moves, key=lambda x: x["eval"])
        else:
            eval_sorted_moves = tree['moves']

        toMove_sorted_moves = []  # score relativo da db in base a chi deve muovere

        is_white_to_move = node.board().turn
        if is_white_to_move:
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
            is_white_to_move=is_white_to_move,
            is_white_repertoire=self.is_white_repertoire)

    def __update_UI(self, child_node, move, full_move_info):
        global OPEN_MOVES
        global UI_UPDATES

        self.open_moves.append(OPEN_MOVES)
        self.ui_updates.append(UI_UPDATES)

        board_info = format_move_infos(
            self.start_time, child_node, move, full_move_info)
        board = str(child_node.board())
        board = get_stylish_chessboard(board)
        open_moves_plot = plot_open_moves(self.ui_updates, self.open_moves)
        board_and_info = align_printables([board, board_info, open_moves_plot])
        clear_and_print(board_and_info)

        if self.options['plot']:
            move_hist = ply_hist(self.stats, max_depth=self.config.MaxDepth)
            white_perc_plot = plot_white_perc(
                self.stats, max_depth=self.config.MaxDepth)
            engine_eval_plot = plot_engine_eval(
                self.stats, max_depth=self.config.MaxDepth)

            plots = align_printables(
                [white_perc_plot, engine_eval_plot, move_hist])
            print(plots)

        UI_UPDATES += 1

    def __check_for_transposition(self, move_san, child_node):
        board = child_node.board()
        board.push_san(move_san)
        fen_position = board.fen()
        if fen_position in self.nodes_fen:
            return True

    def __ask_lichess_api(self, api_url, api_params):
        global GRACEFULL_EXIT

        # reduce the request rate to delay the ip ban...no better solution for
        # the moment
        time.sleep(0.5)
        response = self.session.get(api_url, params=api_params)
        if response.status_code == 429:
            self.logger.error("Request timeout")
            raise KeyboardInterrupt
        else:
            return response
