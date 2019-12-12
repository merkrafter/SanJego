from typing import List, Tuple, Union

from sanjego.gameobjects import Move
from searching.util import GameNode, SearchCallback


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
