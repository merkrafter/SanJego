class Node:
    """
    Represents a state of the game.
    It currently is only a dummy implementation.
    """

    def __init__(self, item):
        """
        Creates a new Node by setting the item.
        """
        self.item = item

    def children(self):
        """
        This method is a generator that yields each child that this node has.
        """
        yield Node(2 * self.item)
        yield Node(2 * self.item + 1)

    def value(self):
        """
        Computes the value of this Node.
        :return: this Node's item
        """
        return self.item

    def is_terminal(self):
        """
        This method computes whether this Node has children.
        :return: False (as this is a dummy implementation)
        """
        return False


def alpha_beta_search(node, depth, alpha=-float('inf'), beta=float('inf'), maximising_player=True):
    """
    Calculates the game value from a given `node` searching at most `depth` levels utilizing a usual alpha beta pruning.
    :param node: a `Node` instance
    :param depth: how many levels to search
    :param alpha:
    :param beta:
    :param maximising_player: True by default
    :return: the value of the game until the current depth
    """
    # print("{} encountered node with value {} while alpha={}, beta={}".format(("min", "max")[maximising_player], node.item, alpha, beta))
    if depth == 0 or node.is_terminal():
        return node.value()
    if maximising_player:
        value = -float('inf')
        for child in node.children():
            value = max(value, alpha_beta_search(child, depth - 1, alpha, beta, not maximising_player))
            alpha = max(alpha, value)
            if alpha >= beta:
                break
        return value
    else:  # maximising_player is False
        value = float('inf')
        for child in node.children():
            value = min(value, alpha_beta_search(child, depth - 1, alpha, beta, not maximising_player))
            beta = min(beta, value)
            if alpha >= beta:
                break
        return value


if __name__ == "__main__":
    print(alpha_beta_search(Node(1), 3))
