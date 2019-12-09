import sys
from typing import List

from sacred import Experiment
from sacred.observers import FileStorageObserver

from src.GameOfSanJego import GameField, Move
from src.Rulesets import BaseRuleSet, KingsRuleSet, MoveOnOpposingOnlyRuleSet, MajorityRuleSet, FreeRuleSet
from src.Searching import alpha_beta_search, CountCallback, GameNode

ex = Experiment()
ex.observers.append(FileStorageObserver('results'))

# for visually separating sections in the output
SEP_SYMBOL = "="
SEP_LENGTH = 25


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


def print_move_list(move_list: List[Move], max_player: bool):
    """
    Prints the move list in the following format:
    # max_player_move min_player_move
    with # being a number starting with 1
    """
    offset = 0  # the first index with max_player's move

    # align the list to max_player starting
    if not max_player:
        offset = 1
        print(f"1: ...             \t {move_list[0]}")

    for nr in range(offset, len(move_list), 2):
        max_move = move_list[nr]
        try:
            min_move = move_list[nr + 1]
        except IndexError:
            if max_move.is_skip_move():
                break
            min_move = Move.skip()
        print(f"{nr // 2 + 1 + offset}: {max_move}\t {min_move}")


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
    print(SEP_SYMBOL * SEP_LENGTH)
    print(f"Calculating the '{rules}' game value for a field of size {height} x {width}:")
    if verbose:
        print(game_field)
    value, move_list = alpha_beta_search(node=start_node, depth=depth, callback=callback, trace_moves=True)
    print(SEP_SYMBOL * SEP_LENGTH)
    print(f"Searched {callback.counter} nodes")
    print(SEP_SYMBOL * SEP_LENGTH)
    print("Optimal moves:")
    print_move_list(move_list, max_player_starts)
    print(SEP_SYMBOL * SEP_LENGTH)

    return value
