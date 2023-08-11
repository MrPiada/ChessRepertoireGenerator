import os
from enum import Enum


class Color(Enum):
    WHITE = 0
    BLACK = 1


def align_printables(lists, width=40):
    aligned_lines = []

    # Split each list into lines
    split_lists = [lst.split('\n') for lst in lists]

    # Find the maximum number of lines in any list
    max_lines = max(len(lst) for lst in split_lists)

    for line_idx in range(max_lines):
        aligned_line = ""
        for lst in split_lists:
            if line_idx < len(lst):
                aligned_line += lst[line_idx].ljust(width)
            else:
                aligned_line += " " * width
            aligned_line += " "  # Add a space between aligned columns
        aligned_lines.append(aligned_line)

    return '\n'.join(aligned_lines)


def clear_and_print(snapshot):
    os.system("clear")
    print(snapshot)
