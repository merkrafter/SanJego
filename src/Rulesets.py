from typing import Tuple

from src.GameOfSanJego import GameField


class BaseRuleSet(object):
    """
    This class provides methods that define the rules of the game and its win conditions.
    """

    def __init__(self, game_field: GameField) -> None:
        """
        Creates a new rule set based on the given game field.
        :param game_field: the game field that the decisions are based on
        """
        self.game_field = game_field

    def allows_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], player: int) -> bool:
        """
        Decides whether the given player is allowed to make the move given by the two positions on the board.
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :param player: ID of a player that is registered in the `GameField` instance of this `RuleSet`
        :return: whether the player is allowed to make this move given this rule set
        """
        pass

