from typing import Iterator, List, Tuple, Union

from sanjego.GameOfSanJego import GameField, Move
from src.Rulesets import BaseRuleSet


class GameNode(object):
    """
    Represents a state of San Jego. It provides methods to iterate over all descending game states, and receive the
    value of this game state.
    """

    def __init__(self, game_field: GameField, rule_set_type: type(BaseRuleSet), move: Move = None,
                 max_player: bool = True,
                 skipped_before: bool = False) -> None:
        """
        Creates a new `GameNode` by setting the game field, rule set and player given as arguments.
        If `player` is omitted, it is set to `game_field`'s `player1` attribute.
        :param skipped_before: for internal use only; is `True` if this is a skipping move
        :param game_field:
        :param rule_set_type: a subtype of BaseRuleSet (or BaseRuleSet itself)
        :param move: stores information on how this game node was derived from the previous one
        :param max_player: whether the maximising player moves next
        """
        # both parameters can not be None, because it is not clear what RuleSet to use in that case
        self.skipped_before = skipped_before
        self.game_field = game_field
        self.move = move
        self.rule_set_type = rule_set_type
        self.rule_set = rule_set_type(game_field)
        self.max_player = max_player
        if self.max_player:
            self.player = self.game_field.player1
        else:
            self.player = self.game_field.player2

    def _children(self) -> Iterator[Tuple['GameNode', float]]:
        """
        Iterates over all possible/allowed following game states and returns those states along with their heuristics.
        :return: iterator over all tuples of following game states and their heuristic values
        """
        count = 0
        # iterate over any position on the field
        # list() needed to copy all the field's positions; they are modified by making moves
        for from_pos in list(self.game_field.field):

            # iterate over the king's neighbourhood of from_pos...
            for to_pos in [(x, y) for x in [from_pos[0] - 1, from_pos[0], from_pos[0] + 1]
                           for y in [from_pos[1] - 1, from_pos[1], from_pos[1] + 1]]:
                move = Move(from_pos, to_pos)

                # ... and yield any allowed moves
                if self.rule_set.allows_move(self.player, move=move):
                    count += 1
                    gn = GameNode(self.game_field, self.rule_set_type, move, not self.max_player, skipped_before=False)
                    gn.make_move()  # needs to be done here already to allow proper sorting
                    heur_val = gn.heuristic_value()
                    # Now the move must be taken back, because otherwise following iterations won't work.
                    # This is inefficient as the move must be made again in the alpha_beta_search but it's still faster
                    # than copying the board.
                    gn.take_back_move()
                    yield gn, heur_val

        if count == 0 and not self.skipped_before:  # game ends if both players can not move
            # maybe the skipping move can be done implicitly like so:
            # for child in GameNode(gf, RuleSet(gf), not self.max_player, skipped_before=True).children():
            #    yield child
            # however, this could conflict with the alpha beta search (moving player)
            gn = GameNode(self.game_field, self.rule_set_type, Move.skip(), not self.max_player, skipped_before=True)
            heur_val = gn.heuristic_value()  # no need to actually make the move as it is a skip anyway
            yield gn, heur_val

    def children(self) -> Iterator['GameNode']:
        """
        Iterates over all possible/allowed following game states.
        :return: iterator over all following game states
        """
        # _children returns (child, val)
        if self.max_player:
            return map(lambda x: x[0], sorted(self._children(), key=lambda x: x[1], reverse=True))  # high to low values
        else:
            return map(lambda x: x[0],
                       sorted(self._children(), key=lambda x: x[1], reverse=False))  # low to high values

    def heuristic_value(self) -> float:
        """
        Computes a heuristic value of this `GameNode` that is used for sorting the nodes but does not necessarily
        represents the actual value of the underlying board.
        This heuristic will make use of the `move` attribute if it is not None to rate boards higher that arose from
        making a move in the middle of the board.
        """
        # the basic idea is to lay more weight on moves that happen in the middle of the board,
        # as they seem to be more important in terms of the outcome of the game

        # heuristic does only apply to real moves
        if self.move is not None and not self.move.is_skip_move():
            x, y = self.move.from_pos
            h = self.game_field.height
            w = self.game_field.width

            # bias values are high in the middle of the board and low at the border
            # depend on the actual board size, hence are affecting even the end game due to high values
            bias_x = h - abs(x - h / 2)
            bias_y = w - abs(y - w / 2)

            # normalized biases, which should only affect the opening but get nearly irrelevant in the end game
            # difference in terms of nodes searched using these is narrow
            # bias_x = 1 - abs(x - h / 2)/h
            # bias_y = 1 - abs(y - w / 2)/w

            # counter-intuitive logic because the MOVE that led to this node is rated as well:
            # If `self` is a position for max_player to make the move,
            # it means that a move from min_player led to `self`. Hence, the heuristic must be decreased in order to
            # make `self` more attractive for min_player.
            if self.max_player:
                return self.game_field.value - bias_x - bias_y
            else:
                return self.game_field.value + bias_x + bias_y
        else:
            return self.game_field.value

    def value(self) -> int:
        """
        Computes the value of this `GameNode`, defined as the value of its `game_field`.
        :return: value of this node's `game_field`
        """
        return self.game_field.value

    def make_move(self) -> None:
        """
        Wrapper to make the move of this instance on the game_field of this instance.
        """
        self.game_field.make_move(move=self.move)

    def take_back_move(self) -> None:
        """
        Wrapper to take back the move of this instance on the game_field of this instance.
        """
        self.game_field.take_back(self.move)

    def __str__(self) -> str:
        """
        Returns a string representation of this game node that contains the player to move and the game field string.
        :return: a string representation of this game node
        """
        return f"turn of player {self.player}\n" + self.game_field.__str__()


class SearchCallback(object):
    """
    This class serves as an abstract base class for every callback class that is suitable for the alpha beta search.
    """

    def callback(self, node: GameNode, depth: int, alpha: float, beta: float, maximising_player: bool) -> None:
        """
        This method will be called once at the beginning of an alpha_beta_search invocation.
        """
        pass


class CountCallback(SearchCallback):
    """
    This class implements a counter for all calls to callback().
    """

    def __init__(self):
        """
        Creates a new CountCallback by initializing the internal `counter` with 0.
        """
        self.counter = 0

    def callback(self, node: GameNode, depth: int, alpha: float, beta: float, maximising_player: bool) -> None:
        """
        Increases the internal counter by 1, ignoring all arguments to this method.
        """
        self.counter += 1


def alpha_beta_search(node: GameNode, depth: int, alpha: float = -float('inf'), beta: float = float('inf'),
                      maximising_player: bool = True,
                      callback: SearchCallback = None,
                      trace_moves: bool = False) -> Union[float, Tuple[float, List[Move]]]:
    """
    Calculates the game value from a given `node` searching at most `depth` levels utilizing alpha beta pruning.
    :param node: a `Node` instance
    :param depth: how many levels to search
    :param alpha:
    :param beta:
    :param maximising_player: True by default
    :param callback: Callback class that is called at the beginning of each function call
    :param trace_moves: whether to return a list of the optimal moves; will be computed either way
    :return: the value of the game until the current depth, and optionally a list of optimal moves
    """
    ###################
    # handling the callback object
    if callback is not None:
        callback.callback(node, depth, alpha, beta, maximising_player)

    ###################
    # overall idea with trace_moves: every alpha_beta_search call takes the move list from its best child
    # and adds the move that led to *this* search function call to the beginning of the move list

    # recursion anchor: depth reached
    if depth == 0:
        if trace_moves:
            return node.value(), [node.move]  # only this search function call can be considered
        return node.value()

    num_children = 0

    ###################
    if maximising_player:
        value = -float('inf')
        best_move_list = []

        for child in node.children():
            num_children += 1
            child.make_move()  # make move (just making this call more visible)
            _value, move_list = alpha_beta_search(child, depth - 1, alpha, beta, not maximising_player, callback, True)
            value = max(value, _value)
            child.take_back_move()  # take back (just making this call more visible)
            if value > alpha:
                alpha = value
                best_move_list = move_list
            # prune the search tree
            if alpha >= beta:
                break

        # node.move is None indicates that this is the root function call
        if node.move is not None:
            best_move_list.insert(0, node.move)

        # this is a leaf node
        if num_children == 0:
            if trace_moves:
                # move list consist only of *this* search function call due to the insertion above
                return node.value(), best_move_list
            return node.value()

        if trace_moves:
            return value, best_move_list
        return value

    ###################
    # maximising_player is False
    else:
        value = float('inf')
        best_move_list = []

        for child in node.children():
            num_children += 1
            child.make_move()  # make move (just making this call more visible)
            _value, move_list = alpha_beta_search(child, depth - 1, alpha, beta, not maximising_player, callback, True)
            value = min(value, _value)
            child.take_back_move()  # take back (just making this call more visible)
            if value < beta:
                beta = value
                best_move_list = move_list
            # prune the search tree
            if alpha >= beta:
                break

        # node.move is None indicates that this is the root function call
        if node.move is not None:
            best_move_list.insert(0, node.move)

        # this is a leaf node
        if num_children == 0:
            if trace_moves:
                # move list consist only of *this* search function call due to the insertion above
                return node.value(), best_move_list
            return node.value()

        if trace_moves:
            return value, best_move_list
        return value
