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
        This basic implementation allows any two towers to be moved on top of each other if their positions meet either
        vertically or horizontally (quad neighbourhood).
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :param player: ID of a player that is registered in the `GameField` instance of this `RuleSet`
        :return: whether the player is allowed to make this move given this rule set
        """
        # perform basic checks
        if not self.basically_allows_move(from_pos, to_pos):
            return False

        # check movement rule (quad neighbourhood) using manhattan distance
        if abs(from_pos[0] - to_pos[0]) + abs(from_pos[1] - to_pos[1]) > 1:
            return False

        return True

    def basically_allows_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int]) -> bool:
        """
        This method performs basic checks on the move that likely apply to all rule sets.
        In detail, it checks whether:
         - both positions are not `None`
         - both positions are different from each other
         - both positions lie on the field
         - there are towers on both positions
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :return: whether the above conditions are fulfilled by the given positions
        """
        # check whether both positions are not None
        if from_pos is None or to_pos is None:
            return False

        # check whether both positions are different from each other
        if from_pos == to_pos:
            return False

        # check whether both positions are on the board and
        # check whether there are towers on both positions
        top_tower = self.game_field.get_tower_at(from_pos)  # would return None if not on the board
        lower_tower = self.game_field.get_tower_at(to_pos)
        if top_tower is None or lower_tower is None or top_tower.height == 0 or lower_tower.height == 0:
            return False

        return True


class KingsRuleSet(BaseRuleSet):
    """
    Using this rule set, a player may move its towers diagonally, effectively allowing an eighth neighbourhood.
    This is also known as the king's neighbourhood (derived from chess).
    """

    def allows_move(self, from_pos, to_pos, player):
        """
        Allows players to move a tower into its king's neighbourhood, that is the 8 fields directly adjacent to it.
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :param player: ID of a player
        :return: whether the player is allowed to make this move given this rule set
        """
        if not self.basically_allows_move(from_pos, to_pos):
            return False

        # both coordinates may differ by at most 1
        if abs(from_pos[0] - to_pos[0]) > 1 or abs(from_pos[1] - to_pos[1]) > 1:
            return False

        return True


class MoveOnOpposingOnlyRuleSet(BaseRuleSet):
    """
    Using this rule set, own towers may only be moved on top of opposing towers.
    """

    def allows_move(self, from_pos, to_pos, player):
        """
        Allows players to move a tower only on top of opposing towers.
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :param player: ID of a player
        :return: whether the player is allowed to make this move given this rule set
        """
        if not super().allows_move(from_pos, to_pos, player):
            return False

        # the above line ensures that there actually are towers at the given positions
        if self.game_field.get_tower_at(from_pos).owner == self.game_field.get_tower_at(to_pos).owner:
            return False

        return True
