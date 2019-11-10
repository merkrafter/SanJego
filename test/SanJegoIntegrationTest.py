import unittest

from src.GameOfSanJego import GameField, GameNode, RuleSet, Tower
from src.Searching import alpha_beta_search


class TestSanJego(unittest.TestCase):
    """
    The test cases of this class test the alpha_beta_search function on San Jego game nodes.
    """

    def test_1x1_field_state(self) -> None:
        """
        The alpha_beta_search's return value for a 1x1 field should be equal to the underlying node's value.
        """
        maximising_player = True

        gf = GameField(1, 1)
        rs = RuleSet(gf)
        node = GameNode(gf, rs, max_player=maximising_player)
        expected_value = node.value()
        for depth in range(5):
            with self.subTest(f"depth {depth}"):
                actual_value = alpha_beta_search(node, depth=depth, maximising_player=maximising_player)
                self.assertEqual(expected_value, actual_value, "wrongly calculated game value")

    def test_end_state(self) -> None:
        """
        The alpha_beta_search's return value for an end state should be equal to the underlying node's value.
        The test field contains towers that each player is not allowed to move, because of the different owner rule and
        because of the majority-to-move rule.
        """
        player1 = 0
        player2 = 1

        gf = GameField.setup_field({
            # first column
            (1, 0): Tower(structure=[player2] * 2 + [player1]),  # (1,0) -> (2,0) is not possible because of same owners
            (2, 0): Tower(owner=player2),
            # next column; separated with a blank column
            (1, 2): Tower(structure=[player1] * 3),  # (1,2) -> (2,2) not possible because of same owners
            (2, 2): Tower(owner=player1)
        })

        for maximising_player in [True, False]:
            if maximising_player:
                gf.set_tower_at((0, 1), Tower(structure=[player1] + [player2] * 2))
            else:
                gf.set_tower_at((0, 1), Tower(structure=[player2] + [player1] * 2))

            # field visually
            #         | [x,y,y] |           x=0 and y=1 if it's player 0's turn and vice versa
            # [1,1,0] |         | [0,0,0]
            # [1]     |         | [0]

            rs = RuleSet(gf)
            node = GameNode(gf, rs, max_player=maximising_player)
            expected_value = node.value()
            for depth in range(5):
                with self.subTest(f"depth {depth} as {('min', 'max')[maximising_player]}"):
                    actual_value = alpha_beta_search(node, depth=depth, maximising_player=maximising_player)
                    self.assertEqual(expected_value, actual_value, "wrongly calculated game value")

    def test_one_forced_move(self) -> None:
        """
        The alpha_beta_search method should return the correct game value if there is only one (forced) move.
        """
        player1 = 0
        player2 = 1
        # [0] | [1]
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 1): Tower(owner=player2)
        })

        expected_values = (-2, 2)  # (min starts, max starts)
        for maximising_player in [True, False]:
            rs = RuleSet(gf)
            node = GameNode(gf, rs, max_player=maximising_player)
            expected_value = expected_values[maximising_player]
            for depth in range(1, 5):  # depth 0 would only calculate the current value (==0)
                with self.subTest(f"depth {depth} as {('min', 'max')[maximising_player]}"):
                    actual_value = alpha_beta_search(node, depth=depth, maximising_player=maximising_player)
                    self.assertEqual(expected_value, actual_value, "wrongly calculated game value")

    def test_two_forced_moves(self) -> None:
        """
        The alpha_beta_search method should return the correct game value if there are only (two) forced moves.
        """
        player1 = 0
        player2 = 1
        # [0] |     | [1]
        #     | [1] |
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 2): Tower(owner=player2),
            (1, 1): Tower(owner=player2)
        })

        expected_values = (-2, -3)  # (min starts, max starts)
        for maximising_player in [True, False]:
            rs = RuleSet(gf)
            node = GameNode(gf, rs, max_player=maximising_player)
            expected_value = expected_values[maximising_player]
            for depth in range(2, 5):  # depth < 2 would only not calculate the correct value
                with self.subTest(f"depth {depth} as {('min', 'max')[maximising_player]}"):
                    actual_value = alpha_beta_search(node, depth=depth, maximising_player=maximising_player)
                    self.assertEqual(expected_value, actual_value, "wrongly calculated game value")

    def test_three_forced_moves(self) -> None:
        """
        The alpha_beta_search method should return the correct game value if there are only (three) forced moves.
        """
        player1 = 0
        player2 = 1
        # [0] | [0] | [1]
        #     | [1] |
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 1): Tower(owner=player1),
            (0, 2): Tower(owner=player2),
            (1, 1): Tower(owner=player2)
        })

        expected_values = (-3, 3)  # (min starts, max starts)
        for maximising_player in [True, False]:
            rs = RuleSet(gf)
            node = GameNode(gf, rs, max_player=maximising_player)
            expected_value = expected_values[maximising_player]
            for depth in range(3, 5):  # depth < 3 would only not calculate the correct value
                with self.subTest(f"depth {depth} as {('min', 'max')[maximising_player]}"):
                    actual_value = alpha_beta_search(node, depth=depth, maximising_player=maximising_player)
                    self.assertEqual(expected_value, actual_value, "wrongly calculated game value")


if __name__ == '__main__':
    unittest.main()