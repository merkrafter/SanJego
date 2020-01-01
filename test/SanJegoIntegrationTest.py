import unittest

import pytest

from src.GameOfSanJego import GameField, Tower, Move
from src.Rulesets import BaseRuleSet, KingsRuleSet, MoveOnOpposingOnlyRuleSet, FreeRuleSet, MajorityRuleSet
from src.Searching import alpha_beta_search, GameNode


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
        node = GameNode(gf, BaseRuleSet, max_player=maximising_player)
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

            node = GameNode(gf, MoveOnOpposingOnlyRuleSet, max_player=maximising_player)
            expected_value = node.value()
            # depth 0: this node; depth 1: skipped move;
            # depth 2: move of respective opponent that would change game value, hence not covered in this test
            for depth in range(2):
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
            node = GameNode(gf, BaseRuleSet, max_player=maximising_player)
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
        maximising_player = True

        # [0] |     | [1]
        #     | [1] |
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 2): Tower(owner=player2),
            (1, 1): Tower(owner=player2)
        })

        node = GameNode(gf, KingsRuleSet, max_player=maximising_player)
        expected_value = -3
        for depth in range(2, 5):  # depth < 2 would only not calculate the correct value
            with self.subTest(f"depth {depth} as {('min', 'max')[maximising_player]}"):
                actual_value = alpha_beta_search(node, depth=depth, maximising_player=maximising_player)
                self.assertEqual(expected_value, actual_value, "wrongly calculated game value")

    @unittest.skip("It might be impossible to create a sequence of 3 forced moves")
    def test_three_forced_moves(self) -> None:
        """
        The alpha_beta_search method should return the correct game value if there are only (three) forced moves.
        """
        player1 = 0
        player2 = 1
        # [0] | [0]   | [0]
        #     | [1,1] |
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),
            (0, 1): Tower(owner=player1),
            (0, 2): Tower(owner=player2),
            (1, 1): Tower(owner=player2)
        })

        expected_values = (-3, 3)  # (min starts, max starts)
        for maximising_player in [True, False]:
            node = GameNode(gf, MoveOnOpposingOnlyRuleSet, max_player=maximising_player)
            expected_value = expected_values[maximising_player]
            for depth in range(3, 5):  # depth < 3 would only not calculate the correct value
                with self.subTest(f"depth {depth} as {('min', 'max')[maximising_player]}"):
                    actual_value = alpha_beta_search(node, depth=depth, maximising_player=maximising_player)
                    self.assertEqual(expected_value, actual_value, "wrongly calculated game value")

    def test_skipping_move(self) -> None:
        """
        The alpha beta search method should handle skipping moves correctly.
        A move must be skipped, if there is no allowed move for a player, but the opposing player may still move.
        """
        player1 = 0
        player2 = 1
        maximising_player = True

        # [0] | [0, 1, 1] | [1]
        gf = GameField.setup_field({
            (0, 0): Tower(owner=player1),  # (0,0) -> (0,1) is illegal
            (0, 1): Tower(structure=[player1] + [player2] * 2),  # player1 may not move this
            (0, 2): Tower(owner=player2)
        })
        self.assertTrue(maximising_player, "misconfigured test: it should be player1's (max) move")

        expected_value = 4
        node = GameNode(gf, BaseRuleSet, max_player=maximising_player)
        actual_value = alpha_beta_search(node, depth=3, maximising_player=maximising_player)  # depth 3 is enough
        self.assertEqual(expected_value, actual_value,
                         f"expected a game value of {expected_value} but got {actual_value}")


class TestMoveLists(unittest.TestCase):
    """
    This test class covers (rather) long-running test cases that run whole board calculations and verify the results.
    """

    def test_base_2x2(self) -> None:
        """
        The optimum for a 2x2 game field with the base ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 0) -> (0, 0)
        2: (0, 1) -> (0, 0)      <skip>
        with a final game value of 4.
        """
        height = 2
        width = 2
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 0), (0, 0)),
                              Move((0, 1), (0, 0)), Move.skip()]
        expected_value = 4

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, BaseRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_base_2x3(self) -> None:
        """
        The optimum for a 2x3 game field with the base ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 2) -> (0, 2)
        2: (0, 1) -> (0, 2)      (1, 0) -> (0, 0)
        with a final game value of 2.
        """
        height = 2
        width = 3
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 2), (0, 2)),
                              Move((0, 1), (0, 2)), Move((1, 0), (0, 0)),
                              Move.skip()]
        expected_value = 2

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, BaseRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    @pytest.mark.slow
    def test_base_3x4(self) -> None:
        """
        The optimum for a 3x4 game field with the base ruleset looks like:
        1: (1, 1) -> (1, 2)      (2, 1) -> (2, 2)
        2: (1, 3) -> (0, 3)      (0, 1) -> (0, 0)
        3: (1, 2) -> (0, 2)      (2, 2) -> (2, 3)
        4: (0, 2) -> (0, 3)      (1, 0) -> (0, 0)
        with a final game value of 2.
        """
        height = 3
        width = 4
        max_player_starts = True

        expected_move_list = [Move((1, 1), (1, 2)), Move((2, 1), (2, 2)),
                              Move((1, 3), (0, 3)), Move((0, 1), (0, 0)),
                              Move((1, 2), (0, 2)), Move((2, 2), (2, 3)),
                              Move((0, 2), (0, 3)), Move((1, 0), (0, 0)),
                              Move.skip()]
        expected_value = 2

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, BaseRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_oppose_2x2(self) -> None:
        """
        The optimum for a 2x2 game field with the oppose ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 0) -> (0, 0)
        2: (0, 1) -> (0, 0)      <skip>
        with a final game value of 4.
        """
        height = 2
        width = 2
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 0), (0, 0)),
                              Move((0, 1), (0, 0)), Move.skip()]
        expected_value = 4

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, MoveOnOpposingOnlyRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_oppose_2x3(self) -> None:
        """
        The optimum for a 2x3 game field with the oppose ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 2) -> (0, 2)
        2: (0, 1) -> (0, 2)      (1, 0) -> (0, 0)
        with a final game value of 2.
        """
        height = 2
        width = 3
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 2), (0, 2)),
                              Move((0, 1), (0, 2)), Move((1, 0), (0, 0)),
                              Move.skip()]
        expected_value = 2

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, MoveOnOpposingOnlyRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_oppose_3x3(self) -> None:
        """
        The optimum for a 3x3 game field with the oppose ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 2) -> (0, 2)
        2: (2, 2) -> (2, 1)      (1, 0) -> (0, 0)
        3: (0, 1) -> (0, 0)      <skip>
        with a final game value of 2.
        """
        height = 3
        width = 3
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 2), (0, 2)),
                              Move((2, 2), (2, 1)), Move((1, 0), (0, 0)),
                              Move((0, 1), (0, 0)), Move.skip()]
        expected_value = 2

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, MoveOnOpposingOnlyRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    @pytest.mark.slow
    def test_oppose_3x4(self) -> None:
        """
        The optimum for a 3x4 game field with the oppose ruleset looks like:
        1: (2, 2) -> (2, 1)      (0, 1) -> (0, 2)
        2: (1, 1) -> (1, 0)      (1, 2) -> (1, 3)
        with a final game value of 0.
        """
        height = 3
        width = 4
        max_player_starts = True

        expected_move_list = [Move((2, 2), (2, 1)), Move((0, 1), (0, 2)),
                              Move((1, 1), (1, 0)), Move((1, 2), (1, 3)),
                              Move.skip()]
        expected_value = 0

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, MoveOnOpposingOnlyRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_kings_2x2(self) -> None:
        """
        The optimum for a 2x2 game field with the kings ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 0) -> (0, 1)
        2: (0, 0) -> (0, 1)      <skip>
        with a final game value of 4.
        """
        height = 2
        width = 2
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 0), (0, 1)),
                              Move((0, 0), (0, 1)), Move.skip()]
        expected_value = 4

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, KingsRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_kings_2x3(self) -> None:
        """
        The optimum for a 2x3 game field with the kings ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 2) -> (0, 1)
        2: (0, 2) -> (0, 1)      (1, 0) -> (0, 1)
        3: (0, 0) -> (0, 1)      <skip>
        with a final game value of 6.
        """
        height = 2
        width = 3
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 2), (0, 1)),
                              Move((0, 2), (0, 1)), Move((1, 0), (0, 1)),
                              Move((0, 0), (0, 1)), Move.skip()]
        expected_value = 6

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, KingsRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    @pytest.mark.slow
    def test_kings_3x3(self) -> None:
        """
        The optimum for a 3x3 game field with the kings ruleset looks like:
        1: (2, 2) -> (1, 2)      (0, 1) -> (1, 1)
        2: (0, 2) -> (1, 1)      (2, 1) -> (2, 0)
        3: (1, 1) -> (1, 0)      (2, 0) -> (1, 0)
        4: (0, 0) -> (1, 0)      <skip>
        with a final game value of 7.
        """
        height = 3
        width = 3
        max_player_starts = True

        expected_move_list = [Move((2, 2), (1, 2)), Move((0, 1), (1, 1)),
                              Move((0, 2), (1, 1)), Move((2, 1), (2, 0)),
                              Move((1, 1), (1, 0)), Move((2, 0), (1, 0)),
                              Move((0, 0), (1, 0)), Move.skip()]
        expected_value = 7

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, KingsRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_free_2x2(self) -> None:
        """
        The optimum for a 2x2 game field with the free ruleset looks like:
        1: (1, 1) -> (0, 1)      (0, 0) -> (0, 1)
        with a final game value of 2.
        """
        height = 2
        width = 2
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((0, 0), (0, 1)),
                              Move.skip()]
        expected_value = 2

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, FreeRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_free_2x3(self) -> None:
        """
        The optimum for a 2x3 game field with the free ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 2) -> (0, 2)
        2: (0, 1) -> (0, 2)      (1, 0) -> (0, 0)
        with a final game value of 2.
        """
        height = 2
        width = 3
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 2), (0, 2)),
                              Move((0, 1), (0, 2)), Move((1, 0), (0, 0)),
                              Move.skip()]
        expected_value = 2

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, FreeRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    @pytest.mark.slow
    def test_free_3x3(self) -> None:
        """
        The optimum for a 3x3 game field with the free ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 2) -> (2, 2)
        2: (0, 0) -> (0, 1)      (2, 1) -> (2, 2)
        3: (0, 1) -> (0, 2)      (1, 0) -> (2, 0)
        with a final game value of 1.
        """
        height = 3
        width = 3
        max_player_starts = True

        # there are multiple ways to achieve the game value
        expected_move_list = [[Move((1, 1), (0, 1)), Move((1, 2), (2, 2)),
                               Move((0, 0), (0, 1)), Move((2, 1), (2, 2)),
                               Move((0, 1), (0, 2)), Move((1, 0), (2, 0)),
                               Move.skip()],
                              [Move((1, 1), (0, 1)), Move((1, 2), (2, 2)),
                               Move((1, 0), (0, 0)), Move((2, 1), (2, 2)),
                               Move((0, 1), (0, 0)), Move.skip()]]
        expected_value = 1

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, FreeRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertIn(move_list, expected_move_list)

    def test_majority_2x2(self) -> None:
        """
        The optimum for a 2x2 game field with the majority ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 0) -> (0, 0)
        2: (0, 1) -> (0, 0)      <skip>
        with a final game value of 4.
        """
        height = 2
        width = 2
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 0), (0, 0)),
                              Move((0, 1), (0, 0)), Move.skip()]
        expected_value = 4

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, MajorityRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    def test_majority_2x3(self) -> None:
        """
        The optimum for a 2x3 game field with the majority ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 2) -> (0, 2)
        2: (0, 1) -> (0, 2)      (1, 0) -> (0, 0)
        with a final game value of 2.
        """
        height = 2
        width = 3
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 2), (0, 2)),
                              Move((0, 1), (0, 2)), Move((1, 0), (0, 0)),
                              Move.skip()]
        expected_value = 2

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, MajorityRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)

    @pytest.mark.slow
    def test_majority_3x3(self) -> None:
        """
        The optimum for a 3x3 game field with the majority ruleset looks like:
        1: (1, 1) -> (0, 1)      (1, 2) -> (2, 2)
        2: (2, 0) -> (1, 0)      (0, 1) -> (0, 2)
        3: (1, 0) -> (0, 0)      (2, 1) -> (2, 2)
        with a final game value of 0.
        """
        height = 3
        width = 3
        max_player_starts = True

        expected_move_list = [Move((1, 1), (0, 1)), Move((1, 2), (2, 2)),
                              Move((2, 0), (1, 0)), Move((0, 1), (0, 2)),
                              Move((1, 0), (0, 0)), Move((2, 1), (2, 2)),
                              Move.skip()]
        expected_value = 0

        game_field = GameField(height=height, width=width)
        start_node = GameNode(game_field, MajorityRuleSet, max_player=max_player_starts)

        depth = 2 * height * width + 1
        value, move_list = alpha_beta_search(node=start_node, depth=depth, maximising_player=max_player_starts,
                                             trace_moves=True)

        self.assertEqual(expected_value, value)
        self.assertEqual(expected_move_list, move_list)


if __name__ == '__main__':
    unittest.main()
