import os

class Report:
    def __init__(self, config, leaves, stats):
        self.config = config
        self.leaves = leaves
        self.dataframestats = stats

    def __compute_scores(self):
        """
        Calculate weighted average engine evaluation and database score.

        Returns:
            tuple: Weighted average engine evaluation score, weighted average database score.
        """
        total_games_sum = sum(leaf.get('tot_games', 0) for leaf in self.leaves)
        weighted_eval = sum(leaf.get('eval', 0) * leaf.get('tot_games', 0) for leaf in self.leaves)/total_games_sum
        weighted_db_score = sum(leaf.get('strongest_practical', 0) * leaf.get('tot_games', 0) for leaf in self.leaves)/total_games_sum
        return weighted_eval, weighted_db_score

    def evaluate_repertoire(self):
        weighted_eval, weighted_db_score = self.__compute_scores()
        os.system("clear")
        print("\n  ########## REPORT\n")
        print(f"  Repertoire: {self.config.PgnName}")
        print(f"  Engine weighted average score: {weighted_eval:.2f}")
        print(f"  LichessDB weighted average score: {weighted_db_score:.1f}%")
        print("\n")
