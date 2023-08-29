import os
import time

from enum import Enum
from tabulate import tabulate
from colorama import Back, init, Style

CHESS_SYMBOLS = {
        'r': '♖', 'n': '♘', 'b': '♗', 'q': '♕', 'k': '♔', 'p': '♙',
        'R': '♜', 'N': '♞', 'B': '♝', 'Q': '♛', 'K': '♚', 'P': '♟',
        '.': ' '
    }
BOARD_SYMBOLS = "rnbqkpRNBQKP."  
TRANSLATOR = BOARD_SYMBOLS.maketrans(CHESS_SYMBOLS) 

class Color(Enum):
    WHITE = 0
    BLACK = 1


def get_stylish_chessboard(encoded_position_str):
    return encoded_position_str.translate(TRANSLATOR)


def align_printables(lists, width=40):
    aligned_lines = ['\n']

    # Split each list into lines
    split_lists = [lst.split('\n') for lst in lists]

    # Find the maximum number of lines in any list
    max_lines = max(len(lst) for lst in split_lists)

    for line_idx in range(max_lines):
        aligned_line = ""
        for lst in split_lists:
            if line_idx < len(lst):
                aligned_line += '\t' + lst[line_idx].ljust(width)
            else:
                aligned_line += '\t' + " " * width
            aligned_line += " "  # Add a space between aligned columns
        aligned_lines.append(aligned_line)

    aligned_lines.append('\n')

    return '\n'.join(aligned_lines)


def clear_and_print(snapshot):
    os.system("clear")
    print(snapshot)


def format_move_infos(start_time, child_node, move, full_move_info):

    elapsed_time = time.time() - start_time
    minutes, seconds = divmod(elapsed_time, 60)
    str_time = f"{minutes:.0f}m{seconds:.0f}s"

    ply = child_node.ply()
    move_number = (ply + 1) // 2
    is_white_to_move = child_node.board().turn
    str_move = str(move_number) + "."
    if is_white_to_move:
        str_move += " ... "
    str_move += move

    move_perc, move_games, engine_eval, move_score = None, None, None, None
    if full_move_info is not None:
        move_perc = str(full_move_info.get('perc')) + "%"
        move_games = full_move_info.get('tot_games')
        engine_eval = full_move_info.get('eval')
        move_score = f"{full_move_info.get('white')}/{full_move_info.get('draws')}/{full_move_info.get('black')}"

    data = [
        ["Elapsed time", str_time],
        ["Ply", ply],
        ["Move", str_move],
        ["Move freq", move_perc],
        ["#Games", move_games],
        ["EngineEval", engine_eval],
        ["MoveScore", move_score]
    ]

    return tabulate(data, tablefmt="plain")


def is_uci_move(move):
    return len(move) == 4 and all(
        char in 'abcdefgh12345678' for char in move)
