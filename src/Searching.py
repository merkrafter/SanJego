import copy
from abc import abstractmethod
from typing import Iterator

from src.GameOfSanJego import GameField
from src.Rulesets import BaseRuleSet


class GameNode(object):
    """
    Represents a state of San Jego. It provides methods to iterate over all descending game states, and receive the
    value of this game state.
    """

    def __init__(self, game_field: GameField, rule_set_type: type(BaseRuleSet), max_player: bool = True,
                 skipped_before: bool = False) -> None:
        """
        Creates a new `GameNode` by setting the game field, rule set and player given as arguments.
        If `player` is omitted, it is set to `game_field`'s `player1` attribute.
        :param skipped_before: for internal use only; is `True` if this is a skipping move
        :param game_field:
        :param rule_set_type: a subtype of BaseRuleSet (or BaseRuleSet itself)
        :param max_player: whether the maximising player moves next
        """
        # both parameters can not be None, because it is not clear what RuleSet to use in that case
        self.skipped_before = skipped_before
        self.game_field = game_field
        self.rule_set_type = rule_set_type
        self.rule_set = rule_set_type(game_field)
        self.max_player = max_player
        if self.max_player:
            self.player = self.game_field.player1
        else:
            self.player = self.game_field.player2

    def _children(self) -> Iterator['GameNode']:
        """
        Iterates over all possible/allowed following game states.
        :return: iterator over all following game states
        """
        count = 0
        # iterate over any position on the field
        for from_pos in [(x, y) for x in range(self.game_field.height) for y in range(self.game_field.width)]:

            # iterate over the king's neighbourhood of from_pos...
            for to_pos in [(x, y) for x in [from_pos[0] - 1, from_pos[0], from_pos[0] + 1]
                           for y in [from_pos[1] - 1, from_pos[1], from_pos[1] + 1]]:

                # ... and yield any allowed moves
                if self.rule_set.allows_move(self.player, from_pos, to_pos):
                    gf = copy.deepcopy(self.game_field)
                    gf.make_move(from_pos, to_pos)
                    count += 1
                    yield GameNode(gf, self.rule_set_type, not self.max_player, skipped_before=False)
        if count == 0 and not self.skipped_before:  # game ends if both players can not move
            # maybe the skipping move can be done implicitly like so:
            # for child in GameNode(gf, RuleSet(gf), not self.max_player, skipped_before=True).children():
            #    yield child
            # however, this could conflict with the alpha beta search (moving player)
            gf = copy.deepcopy(self.game_field)
            yield GameNode(gf, self.rule_set_type, not self.max_player, skipped_before=True)

    def children(self) -> Iterator['GameNode']:
        """
        Iterates over all possible/allowed following game states.
        :return: iterator over all following game states
        """
        if self.max_player:
            return sorted(self._children(), key=lambda x: x.value(), reverse=True)  # high to low values
        else:
            return sorted(self._children(), key=lambda x: x.value(), reverse=False)  # low to high values

    def value(self) -> int:
        """
        Computes the value of this `GameNode`, defined as the value of its `game_field`.
        :return: value of this node's `game_field`
        """
        return self.game_field.value

    def __str__(self) -> str:
        """
        Returns a string representation of this game node that contains the player to move and the game field string.
        :return: a string representation of this game node
        """
        return f"turn of player {self.player}\n" + self.game_field.__str__()


class SearchCallback(object):
    @abstractmethod
    def callback(self, node: GameNode, depth: int, alpha: int, beta: int, maximising_player: bool) -> None:
        pass


class CountCallback(SearchCallback):
    def __init__(self):
        self.counter = 0

    def callback(self, node: GameNode, depth: int, alpha: int, beta: int, maximising_player: bool) -> None:
        self.counter += 1


def alpha_beta_search(node: GameNode, depth: int, alpha: float = -float('inf'), beta: float = float('inf'),
                      maximising_player: bool = True,
                      callback: SearchCallback = None) -> float:
    """
    Calculates the game value from a given `node` searching at most `depth` levels utilizing a usual alpha beta pruning.
    :param node: a `Node` instance
    :param depth: how many levels to search
    :param alpha:
    :param beta:
    :param maximising_player: True by default
    :param callback: Callback class that is called at the beginning of each function call
    :return: the value of the game until the current depth
    """
    if callback is not None:
        callback.callback(node, depth, alpha, beta, maximising_player)
    if depth == 0:
        return node.value()
    num_children = 0
    if maximising_player:
        value = -float('inf')
        for child in node.children():
            num_children += 1
            value = max(value, alpha_beta_search(child, depth - 1, alpha, beta, not maximising_player, callback))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        if num_children == 0:
            return node.value()
        return value
    else:  # maximising_player is False
        value = float('inf')
        for child in node.children():
            num_children += 1
            value = min(value, alpha_beta_search(child, depth - 1, alpha, beta, not maximising_player, callback))
            beta = min(beta, value)
            if alpha >= beta:
                break
        if num_children == 0:
            return node.value()
        return value
