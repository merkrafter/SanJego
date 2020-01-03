from typing import Tuple, Dict, Optional

import searching
from rulesets.Rulesets import BaseRuleSet, KingsRuleSet, MoveOnOpposingOnlyRuleSet, MajorityRuleSet, FreeRuleSet
from sanjego.gameobjects import GameField, Tower
from searching.util import GameNode


def fabricate(rules: str, height: int, width: int, max_player_starts: bool,
              game_field_specs: Optional[Dict[Tuple[int, int], Tower]] = None) -> Tuple[GameField, GameNode]:
    """
    Creates a game_field and a game_node from the given arguments.
    Raises RuntimeError if the rules can not be recognized.
    :param rules: the rule set to use
    :param height: the height of the game field
    :param width: the width of the game field
    :param max_player_starts: the amount of consecutive half-moves that will be evaluated at most
    :param game_field_specs: can be used to set up a specific game field directly
    :return: the game field and game node to evaluate
    """
    RULES = {
        'base': BaseRuleSet,
        'kings': KingsRuleSet,
        'oppose': MoveOnOpposingOnlyRuleSet,
        'majority': MajorityRuleSet,
        'free': FreeRuleSet
    }

    if rules not in RULES:
        raise RuntimeError(f"given rule set {rules} not recognised")

    if game_field_specs is None:
        game_field = GameField(height=height, width=width)
    else:
        game_field = GameField.setup_field(game_field_specs, min_height=height, min_width=width)

    if RULES[rules] == KingsRuleSet:
        start_node = GameNode(game_field, RULES[rules], max_player=max_player_starts,
                              neighbourhood=searching.util.kings_neighbourhood)
    else:
        start_node = GameNode(game_field, RULES[rules], max_player=max_player_starts,
                              neighbourhood=searching.util.quad_neighbourhood)

    return game_field, start_node
