from sacred import Experiment

from src.GameOfSanJego import GameField, RuleSet, GameNode
from src.Searching import alpha_beta_search

ex = Experiment()


@ex.config
def config():
    # game relevant
    height = 1
    width = 1
    max_player_starts = True
    max_depth = float('inf')

    # additional configs
    verbose = False


@ex.automain
def main(height: int, width: int, max_player_starts: bool, max_depth: int, verbose: bool):
    # create the necessary objects
    game_field = GameField(height=height, width=width)
    rule_set = RuleSet(game_field)
    start_node = GameNode(game_field, rule_set, max_player=max_player_starts)

    # Each time a player moves, the number of towers on the field is reduced by 1.
    # If in the worst case only one player is able to move, the game is over in at most 2*size_of_the_field moves.
    # ('*2' because the necessary skip of the over player accounts for the depth as well.)
    depth = min(2 * height * width + 1, max_depth)

    # run the actual experiment
    print(f"Calculating the game value for a field of size {height} x {width}:")
    if verbose:
        print(game_field)
    value = alpha_beta_search(node=start_node, depth=depth)
    return value
