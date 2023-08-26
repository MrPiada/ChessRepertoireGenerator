import pandas as pd

from config import StartPositionType
class Report:
    def __init__(self, config, leaves, stats):
        self.config = config
        self.leaves = leaves
        self.datafrastatsme = stats

    def compute_scores(self):
        """
        Calculate weighted average engine evaluation and database score.

        Returns:
            tuple: Weighted average engine evaluation score, weighted average database score.
        """
        total_games_sum = sum(leaf.get('tot_games', 0) for leaf in self.leaves)
        weighted_eval = sum(leaf.get('eval', 0) * leaf.get('tot_games', 0) for leaf in self.leaves)/total_games_sum
        weighted_db_score = sum(leaf.get('strongest_practical', 0) * leaf.get('tot_games', 0) for leaf in self.leaves)/total_games_sum
        return weighted_eval, weighted_db_score

    # def display_dicts(self):
    #     for idx, dictionary in enumerate(self.dict_list, start=1):
    #         print(f"Dictionary {idx}:")
    #         for key, value in dictionary.items():
    #             print(f"  {key}: {value}")