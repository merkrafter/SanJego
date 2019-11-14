from typing import Any, Iterator


class Node:
    """
    Represents a state of the game.
    It currently is only a dummy implementation.
    """

    def __init__(self, item: Any) -> None:
        """
        Creates a new Node by setting the item.
        """
        self.item = item

    def children(self) -> Iterator['Node']:
        """
        This method is a generator that yields each child that this node has.
        """
        yield Node(2 * self.item)
        yield Node(2 * self.item + 1)

    def value(self) -> float:
        """
        Computes the value of this Node.
        :return: this Node's item
        """
        return self.item


class SearchCallback(object):
    @abstractmethod
    def callback(self, node: Node, depth: int, alpha: int, beta: int, maximising_player: bool) -> None:
        pass


def alpha_beta_search(node: Node, depth: int, alpha: float = -float('inf'), beta: float = float('inf'),
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


if __name__ == "__main__":
    print(alpha_beta_search(Node(1), 3))
