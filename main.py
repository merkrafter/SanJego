import sys

from sacred import Experiment
from sacred.observers import FileStorageObserver

from src.GameOfSanJego import GameField
from src.Rulesets import BaseRuleSet, KingsRuleSet, MoveOnOpposingOnlyRuleSet, MajorityRuleSet, FreeRuleSet
from src.Searching import alpha_beta_search, CountCallback, GameNode

ex = Experiment()
ex.observers.append(FileStorageObserver('results'))


@ex.config
def config():
    # game relevant
    rules = 'base'
    height = 1
    width = 1
    max_player_starts = True
    max_depth = float('inf')

    # additional configs
    verbose = False


@ex.automain
def main(rules: str, height: int, width: int, max_player_starts: bool, max_depth: int, verbose: bool):
    RULES = {
        'base': BaseRuleSet,
        'kings': KingsRuleSet,
        'oppose': MoveOnOpposingOnlyRuleSet,
        'majority': MajorityRuleSet,
        'free': FreeRuleSet
    }

    if rules not in RULES:
        sys.stderr.write(f"'{rules}' not recognised. Allowed rules are: ")
        sys.stderr.write(", ".join(RULES.keys()))
        sys.stderr.write("\n")
        exit(1)

    # create the necessary objects
    game_field = GameField(height=height, width=width)
    start_node = GameNode(game_field, RULES[rules], max_player=max_player_starts)

    # Each time a player moves, the number of towers on the field is reduced by 1.
    # If in the worst case only one player is able to move, the game is over in at most 2*size_of_the_field moves.
    # ('*2' because the necessary skip of the over player accounts for the depth as well.)
    depth = min(2 * height * width + 1, max_depth)

    callback = CountCallback()

    # run the actual experiment
    print(f"Calculating the '{rules}' game value for a field of size {height} x {width}:")
    if verbose:
        print(game_field)
    value = alpha_beta_search(node=start_node, depth=depth, callback=callback)
    print(f"Searched {callback.counter} nodes")
    return value
