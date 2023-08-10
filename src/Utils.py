import os
from enum import Enum


class Color(Enum):
    WHITE = 0
    BLACK = 1


def align_plots(
        white_perc_plot,
        engine_eval_plot,
        hist,
        width=40):
    wp = white_perc_plot.split('\n')
    ep = engine_eval_plot.split('\n')
    h = hist.split('\n')

    lines = []

    for l1, l2, l3 in zip(wp, ep, h):
        # Pad each line with spaces
        l1 = l1.ljust(width)
        l2 = l2.ljust(width)
        l3 = l3.ljust(width)
        lines.append(f"{l1}{l2}{l3}")

    return '\n'.join(lines)


def clear_and_print(snapshot):
    os.system("clear")
    print(snapshot)
