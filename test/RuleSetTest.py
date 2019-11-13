from unittest import TestCase

from src.GameOfSanJego import GameField, Tower
from src.Rulesets import BaseRuleSet


class TestBaseRuleSet(TestCase):
    def test_allows_move(self) -> None:
        """
        The rule set should allow a basic move from (0,0) to (0,1) if those positions exist on the board.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)
        rs = BaseRuleSet(gf)
        self.assertTrue(rs.allows_move(from_pos, to_pos, gf.player1))

    def test_does_not_allow_move_outside_field(self) -> None:
        """
        The rule set should not allow moves from or to outside the game field (for any player).
        """
        height = 5
        width = 4
        positions = [(x, y) for x in [-1, 0, height] for y in [-1, 0, width] if not (x == 0 and y == 0)]
        for from_pos in positions:
            for to_pos in positions:
                with self.subTest(f"{from_pos} -> {to_pos}"):
                    gf = GameField(height=height, width=width)
                    rs = BaseRuleSet(gf)
                    self.assertFalse(rs.allows_move(from_pos, to_pos, gf.player1),
                                     f"player {gf.player1} should not be able to move from {from_pos} -> {to_pos}")
                    self.assertFalse(rs.allows_move(from_pos, to_pos, gf.player2),
                                     f"player {gf.player2} should not be able to move from {from_pos} -> {to_pos}")

    def test_does_not_allow_moving_without_towers(self) -> None:
        """
        The rule set should not allow moving from or to positions where no tower is.
        This should be consistent with the `set_tower_at` method.
        """
        from itertools import combinations
        no_tower_pos1 = (1, 1)
        no_tower_pos2 = (1, 2)
        tower_pos = (0, 1)
        positions = [no_tower_pos1, no_tower_pos2, tower_pos]

        gf = GameField(3, 3)
        player1 = gf.player1
        gf.set_tower_at(pos=no_tower_pos1, tower=None)
        gf.set_tower_at(pos=no_tower_pos2, tower=None)
        gf.set_tower_at(pos=tower_pos, tower=Tower(owner=player1))
        rs = BaseRuleSet(gf)

        for (from_pos, to_pos) in combinations(positions, 2):
            with self.subTest(f"{from_pos} -> {to_pos}"):
                self.assertNotEqual(from_pos, tower_pos, "misconfigured test: both positions must not be equal")
                self.assertFalse(rs.allows_move(from_pos, to_pos, player1),
                                 f"should not allow move from {from_pos} -> {to_pos} (missing tower)")

    def test_does_not_allow_diagonal_move(self) -> None:
        """
        Using the base rule set, it should not be allowed to move diagonally.
        """
        x = 1
        y = 1
        positions = [(x + i, y + j) for i in (-1, 1) for j in (-1, 1)]
        from_pos = (x, y)

        gf = GameField(3, 3)
        rs = BaseRuleSet(gf)
        some_player = gf.player1  # not relevant for this test
        for to_pos in positions:
            with self.subTest(f"{from_pos} -> {to_pos}"):
                self.assertFalse(rs.allows_move(from_pos, to_pos, some_player),
                                 f"should not allow move {from_pos} -> {to_pos}")

    def test_should_not_allow_None_positions(self) -> None:
        """
        The rule set should not allow moves that involve a `None` position.
        """
        positions = [None, (0, 0)]

        gf = GameField(2, 2)
        rs = BaseRuleSet(gf)
        some_player = gf.player1

        for from_pos in positions:
            for to_pos in positions:
                if from_pos is None or to_pos is None:  # not both correct positions
                    with self.subTest(f"{from_pos} -> {to_pos}"):
                        self.assertFalse(rs.allows_move(from_pos, to_pos, some_player),
                                         f"should not allow move {from_pos} -> {to_pos}")
