import pstats
from pstats import SortKey

p = pstats.Stats("builder.prof")

p.sort_stats("tottime").print_stats(30)
