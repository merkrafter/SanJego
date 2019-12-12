import unittest

from searching import Searching
from sanjego.gameobjects import Tower, GameField
from rulesets.Rulesets import BaseRuleSet
from searching.util import GameNode


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
        self.move = None  # to be compatible to GameNode

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

    def make_move(self) -> None:
        """
        This method does nothing but fulfill the interface of GameNode
        """
        pass

    def take_back_move(self) -> None:
        """
        This method does nothing but fulfill the interface of GameNode
        """
        pass


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


class TestGameNode(unittest.TestCase):
    def test_children_of_1x1_field(self) -> None:
        """
        A game node should not yield any real children (that is: only skipping) if it contains a 1x1 game field.
        """
        gf = GameField(1, 1)
        for is_max_player in [True, False]:
            with self.subTest(f"as {('min', 'max')[is_max_player]} player"):
                node = GameNode(gf, BaseRuleSet, max_player=is_max_player)
                children = list(node.children())
                self.assertEqual(1, len(children), f"there should be exactly 1 move (skip), but found {len(children)}")
                child = children[0]
                self.assertEqual(gf, child.game_field, "skipping should not alter the game field")
                grandchildren = list(child.children())
                self.assertEqual(0, len(grandchildren), f"there should be no moves, but found {grandchildren}")

    def test_children_without_allowed_move(self) -> None:
        """
        A game node without allowed moves should not have any real children (that is: only skipping).
        """
        player1 = 0
        player2 = 1
        gf = GameField(3, 3)
        # clear field first
        for pos in [(x, y) for x in range(3) for y in range(3)]:
            gf.set_tower_at(pos, None)

        # set two towers that can not be moved onto each other
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (2, 2): Tower(owner=player2)
        })

        for is_max_player in [True, False]:
            with self.subTest(f"as {('min', 'max')[is_max_player]} player"):
                node = GameNode(gf, BaseRuleSet, max_player=is_max_player)
                children = list(node.children())
                self.assertEqual(1, len(children), f"there should be exactly 1 move (skip), but found {len(children)}")
                child = children[0]
                self.assertEqual(gf, child.game_field, "skipping should not alter the game field")
                grandchildren = list(child.children())
                self.assertEqual(0, len(grandchildren), f"there should be no moves, but found {grandchildren}")

    def test_children_with_one_possible_move(self) -> None:
        """
        A game node with one possible move should only have a single child. There are no disallowed moves in this test
        case.
        """
        player1 = 0
        player2 = 1
        gf = GameField(3, 3)
        # clear field first
        for pos in [(x, y) for x in range(3) for y in range(3)]:
            gf.set_tower_at(pos, None)

        # set two towers that can not be moved onto each other
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (1, 1): Tower(owner=player2)
        })

        for is_max_player in [True, False]:
            with self.subTest(f"as {('min', 'max')[is_max_player]} player"):
                node = GameNode(gf, BaseRuleSet, max_player=is_max_player)
                children = list(node.children())
                self.assertEqual(1, len(children), f"this node should have only one child but found {children}")

    def test_children_with_one_allowed_move(self) -> None:
        """
        A game node with one allowed move should only have a single child. There are other moves that are disallowed
        by the rule set in this test case.
        """
        player1 = 0
        player2 = 1

        # set tower constellation to allow one move:
        # (0,0) -> (0,1)
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 1): Tower(structure=[player2] + [player1] * 2),
            (1, 1): Tower(owner=player2)
        })

        node = GameNode(gf, BaseRuleSet)
        children = list(node.children())
        self.assertEqual(1, len(children), f"this node should have only one child but found {children}")

    def test_children_with_two_allowed_moves(self) -> None:
        """
        A game node with two allowed moves should have two children. There is no other move that is disallowed
        in this test case.
        """
        player1 = 0
        player2 = 1

        # set tower constellation to allow two moves:
        # (0,1) -> (0,0) and
        # (0,1) -> (1,1)
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 1): Tower(structure=[player2] * 2 + [player1]),
            (1, 1): Tower(owner=player1)
        })

        node = GameNode(gf, BaseRuleSet, max_player=False)
        children = list(node.children())
        self.assertEqual(2, len(children), f"this node should have two children but found {children}")

    def test_children_with_three_allowed_moves_angle(self) -> None:
        """
        A game node with three allowed moves should have three children. There is no other move that is disallowed
        in this test case.
        """
        player1 = 0
        player2 = 1

        # set tower constellation to allow three moves:
        # (0,0) -> (0,1),
        # (0,1) -> (0,0) and
        # (0,1) -> (1,1)
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 1): Tower(structure=[player1] + [player2] * 2),
            (1, 1): Tower(owner=player2)
        })

        node = GameNode(gf, BaseRuleSet, max_player=True)
        children = list(node.children())
        self.assertEqual(3, len(children), f"this node should have three children but found {children}")

    def test_children_with_three_allowed_moves_row(self) -> None:
        """
        A game node with three allowed moves should have three children. There is no other move that is disallowed
        in this test case.
        """
        player1 = 0
        player2 = 1
        maximising_player = True

        # [0] | [0, 1, 1] | [1]
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),  # (0,0) -> (0,1)
            (0, 1): Tower(structure=[player1] + [player2] * 2),  # (0,1) -> (0,0) and (0,1) -> (0,2)
            (0, 2): Tower(owner=player2)
        })

        node = GameNode(gf, BaseRuleSet, max_player=maximising_player)
        children = list(node.children())
        self.assertEqual(3, len(children), f"this node should have three children but found {children}")

    def test_considers_skipping(self) -> None:
        """
        The game node should consider skipping a move, if there is no allowed move for that active player but the
        opponent can still move.
        """
        player1 = 0
        player2 = 1
        maximising_player = False

        # player2 is to move but can not do anything
        # [0] | [0, 1, 1]
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 1): Tower(structure=[player1] + [player2] * 2),
        })

        node = GameNode(gf, BaseRuleSet, max_player=maximising_player)
        children = list(node.children())
        self.assertEqual(1, len(children), f"there should be exactly 1 move (skip), but found {len(children)}")
        self.assertEqual(gf, children[0].game_field, "skipping should not alter the game field")

        pass


if __name__ == '__main__':
    unittest.main()
