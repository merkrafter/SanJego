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
