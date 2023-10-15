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
        self.leaves = [
            leaf for leaf in self.leaves if leaf.get(
                'eval', 0) != -99.99]
        total_games_sum = sum(leaf.get('tot_games', 0) for leaf in self.leaves)

        if (total_games_sum > 0):
            # TODO: rimuovere valutazione -99.99
            weighted_eval = sum(leaf.get('eval', 0) * leaf.get('tot_games', 0)
                                for leaf in self.leaves) / total_games_sum
            weighted_db_score = sum(
                leaf.get(
                    'strongest_practical',
                    0) * leaf.get(
                    'tot_games',
                    0) for leaf in self.leaves) / total_games_sum
            return weighted_eval, weighted_db_score, total_games_sum
        else:
            return -9999, -9999, -9999

    def evaluate_repertoire(self):
        weighted_eval, weighted_db_score, total_games_sum = self.__compute_scores()
        os.system("clear")
        print("\n  ########## REPORT\n")

        print(f"REPORT: total_games_sum: {total_games_sum}")

        print(f"  Repertoire: {self.config.PgnName}")
        print(f"  Engine weighted average score: {weighted_eval:.2f}")
        print(f"  LichessDB weighted average score: {weighted_db_score:.1f}%")
        print("\n")
