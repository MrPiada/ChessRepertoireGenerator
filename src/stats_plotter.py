import numpy as np
from ap3 import *


def ply_hist(stats, width=30, height=20, max_depth=10):
    if (len(stats) > 0):
        return hist(stats['ply'],
                    histtype='None',
                    return_str=True,
                    shape=(width, height),
                    plot_labels=True,
                    xlabel='ply',
                    ylabel='#moves per ply',
                    xticks_to_int=True,
                    yticks_to_int=True)
    else:
        return ''


def plot_white_perc(stats, width=30, height=20, max_depth=10):
    if (len(stats) > 0):
        white_perc_data = stats.groupby('ply')['whitePerc'].agg(['mean'])
        p = AFigure(
            shape=(
                width,
                height),
            xlabel='ply',
            ylabel=('avg. white %'),
            xticks_to_int=True)
        mid_vals = np.full(max_depth + 1, 50.0)
        xvals = range(max_depth + 1)
        _ = p.plot(xvals, mid_vals, marker='-', plot_slope=True)
        return (
            p.plot(
                white_perc_data.index,
                white_perc_data['mean'],
                marker='o'))
    else:
        return ''


def plot_engine_eval(stats, width=30, height=20, max_depth=10):
    if (len(stats) > 0):
        engine_eval_data = stats[stats['engineEval'] > -
                                 10].groupby('ply')['engineEval'].agg(['mean'])
        p = AFigure(
            shape=(
                width,
                height),
            xlabel='ply',
            ylabel=('avg. engine eval'), xticks_to_int=True)
        return (
            p.plot(
                engine_eval_data.index,
                engine_eval_data['mean'],
                marker='o'))
    else:
        return ''
