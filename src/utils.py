import os
import time
import re

from enum import Enum
from tabulate import tabulate


class Color(Enum):
    WHITE = 0
    BLACK = 1


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


def split_move_comment(move_comment):
    pattern = r'(\d+%)\s*\((\d+)\)(?: -- (-?\d+\.\d+))?(?: -- (\d+/\d+/\d+))?'
    match = re.search(pattern, move_comment)

    if match:
        move_perc = match.group(1) if match.group(1) is not None else None
        move_games = match.group(2) if match.group(2) is not None else None
        engine_eval = match.group(3) if match.group(3) is not None else None
        move_score = match.group(4) if match.group(4) is not None else None

        return move_perc, move_games, engine_eval, move_score
    else:
        return None, None, None, None


def format_move_infos(start_time, child_node, move, move_comment):

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

    move_perc, move_games, engine_eval, move_score = split_move_comment(
        move_comment)

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
