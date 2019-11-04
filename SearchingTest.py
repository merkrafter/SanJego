import unittest

import Searching


class BinaryNode:
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
        yield BinaryNode(2 * self.item)
        yield BinaryNode(2 * self.item + 1)

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


class AlphaBetaSearchTestCases(unittest.TestCase):
    def test_max_returns_root_node_at_depth_0(self):
        self.assertEqual(Searching.alpha_beta_search(BinaryNode(1), depth=0), 1)

    def test_max_returns_higher_of_two_children(self):
        self.assertEqual(Searching.alpha_beta_search(BinaryNode(1), depth=1), 3)

    def test_min_returns_lower_of_two_children(self):
        self.assertEqual(Searching.alpha_beta_search(BinaryNode(1), depth=1, maximising_player=False), 2)

    def test_min_chooses_better_action_at_depth_2(self):
        self.assertEqual(Searching.alpha_beta_search(BinaryNode(1), depth=2), 6)

    def test_max_chooses_better_action_at_depth_3(self):
        self.assertEqual(Searching.alpha_beta_search(BinaryNode(1), depth=3), 13)


if __name__ == '__main__':
    unittest.main()
