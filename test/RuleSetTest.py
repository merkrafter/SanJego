from unittest import TestCase

from sanjego.GameOfSanJego import GameField, Tower, Move
from rulesets.Rulesets import BaseRuleSet, KingsRuleSet, MajorityRuleSet, FreeRuleSet, MoveOnOpposingOnlyRuleSet


class TestBaseRuleSet(TestCase):
    def test_allows_move(self) -> None:
        """
        The rule set should allow a basic move from (0,0) to (0,1) if those positions exist on the board.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)
        for RuleSet in [BaseRuleSet, KingsRuleSet, MajorityRuleSet, FreeRuleSet, MoveOnOpposingOnlyRuleSet]:
            rs = RuleSet(gf)
            with self.subTest(f"{RuleSet.__name__} explicit positions"):
                self.assertTrue(rs.allows_move(gf.player1, from_pos, to_pos))
            with self.subTest(f"{RuleSet.__name__} move objects"):
                self.assertTrue(rs.allows_move(gf.player1, move=Move(from_pos, to_pos)))

    def test_does_not_allow_move_outside_field(self) -> None:
        """
        The rule set should not allow moves from or to outside the game field (for any player).
        """
        height = 5
        width = 4
        positions = [(x, y) for x in [-1, 0, height] for y in [-1, 0, width] if not (x == 0 and y == 0)]
        for from_pos in positions:
            for to_pos in positions:
                for RuleSet in [BaseRuleSet, KingsRuleSet, MajorityRuleSet, FreeRuleSet, MoveOnOpposingOnlyRuleSet]:
                    with self.subTest(f"{from_pos} -> {to_pos} in {RuleSet.__name__}"):
                        gf = GameField(height=height, width=width)
                        rs = RuleSet(gf)
                        self.assertFalse(rs.allows_move(gf.player1, from_pos, to_pos),
                                         f"player {gf.player1} should not be able to move from {from_pos} -> {to_pos}")
                        self.assertFalse(rs.allows_move(gf.player2, from_pos, to_pos),
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

        for RuleSet in [BaseRuleSet, KingsRuleSet, MajorityRuleSet, FreeRuleSet, MoveOnOpposingOnlyRuleSet]:
            rs = RuleSet(gf)
            for (from_pos, to_pos) in combinations(positions, 2):
                with self.subTest(f"explicit: {from_pos} -> {to_pos} in {RuleSet.__name__}"):
                    self.assertNotEqual(from_pos, tower_pos, "misconfigured test: both positions must not be equal")
                    self.assertFalse(rs.allows_move(player1, from_pos, to_pos),
                                     f"should not allow move from {from_pos} -> {to_pos} (missing tower)")
                with self.subTest(f"move: {from_pos} -> {to_pos} in {RuleSet.__name__}"):
                    self.assertNotEqual(from_pos, tower_pos, "misconfigured test: both positions must not be equal")
                    self.assertFalse(rs.allows_move(player1, move=Move(from_pos, to_pos)),
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
        some_player = gf.player1  # not relevant for this test

        # any rule set except king's rule set
        for RuleSet in [BaseRuleSet, MajorityRuleSet, FreeRuleSet, MoveOnOpposingOnlyRuleSet]:
            rs = RuleSet(gf)
            for to_pos in positions:
                with self.subTest(f"explicit: {from_pos} -> {to_pos} in {RuleSet.__name__}"):
                    self.assertFalse(rs.allows_move(some_player, from_pos, to_pos),
                                     f"should not allow move {from_pos} -> {to_pos}")
                with self.subTest(f"move: {from_pos} -> {to_pos} in {RuleSet.__name__}"):
                    self.assertFalse(rs.allows_move(some_player, move=Move(from_pos, to_pos)),
                                     f"should not allow move {from_pos} -> {to_pos}")

    def test_does_not_allow_moving_opposing_towers(self) -> None:
        """
        The rule set should not allow moving opposing towers.
        """
        pos_of_p1_tower = (0, 0)
        pos_of_p2_tower = (0, 1)
        gf = GameField.setup_field({
            pos_of_p1_tower: Tower(owner=0),
            pos_of_p2_tower: Tower(owner=1)
        })

        # except FreeRuleSet
        for RuleSet in [BaseRuleSet, KingsRuleSet, MajorityRuleSet, MoveOnOpposingOnlyRuleSet]:
            with self.subTest(f"{RuleSet.__name__}"):
                rs = RuleSet(gf)
                self.assertFalse(rs.allows_move(player=gf.player2, from_pos=pos_of_p1_tower, to_pos=pos_of_p2_tower),
                                 "player 2 may not move player 1's tower")

                self.assertFalse(rs.allows_move(player=gf.player1, from_pos=pos_of_p2_tower, to_pos=pos_of_p1_tower),
                                 "player 1 may not move player 2's tower")

    def test_player_may_move_tower_with_height_1(self) -> None:
        """
        A player should be allowed to move a tower if he owns the only brick.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        player1 = 1
        some_other_player = 2  # not relevant for this test
        self.assertNotEqual(player1, some_other_player, "misconfigured test: both player IDs should be different")

        subject_tower = Tower(structure=[player1])

        gf = GameField.setup_field({
            from_pos: subject_tower,
            to_pos: Tower(owner=some_other_player)
        })

        # actual test case
        # except FreeRuleSet
        for RuleSet in [BaseRuleSet, MajorityRuleSet, KingsRuleSet, MoveOnOpposingOnlyRuleSet]:
            rs = RuleSet(gf)
            with self.subTest(f"explicit: {RuleSet.__name__}"):
                self.assertTrue(rs.allows_move(player1, from_pos, to_pos),
                                f"player {player1} should be able to move tower {subject_tower}")
                self.assertFalse(rs.allows_move(some_other_player, from_pos, to_pos),
                                 f"player {some_other_player} should not be able to move tower {subject_tower}")
            with self.subTest(f"move: {RuleSet.__name__}"):
                self.assertTrue(rs.allows_move(player1, move=Move(from_pos, to_pos)),
                                f"player {player1} should be able to move tower {subject_tower}")
                self.assertFalse(rs.allows_move(some_other_player, move=Move(from_pos, to_pos)),
                                 f"player {some_other_player} should not be able to move tower {subject_tower}")

    def test_player_may_move_tower_with_half_share(self) -> None:
        """
        Both players should be allowed to move a tower, even if they own only 50% of bricks.
        """
        from itertools import permutations
        from_pos = (0, 0)
        to_pos = (0, 1)
        player1 = 1
        player2 = 2
        self.assertNotEqual(player1, player2, "misconfigured test: both player IDs should be different")

        # multiple tests with shuffled structure
        for structure in permutations([player1] * 2 + [player2] * 2):
            tower = Tower(structure=structure)
            with self.subTest(f"test tower {tower}"):
                gf = GameField(1, 2, player1=player1, player2=player2)
                gf.set_tower_at(from_pos, tower)
                rs = MajorityRuleSet(gf)

                # makes sure the tower at to_pos is an opposing tower
                gf.set_tower_at(to_pos, Tower(owner=player2))
                self.assertTrue(rs.allows_move(player1, from_pos, to_pos),
                                f"player {player1} should be able to move the tower {tower}")

                # makes sure the tower at to_pos is an opposing tower
                gf.set_tower_at(to_pos, Tower(owner=player2))
                self.assertTrue(rs.allows_move(player2, from_pos, to_pos),
                                f"player {player2} should be able to move the tower {tower}")

    def test_player_may_move_tower_with_majority(self) -> None:
        """
        A player should be allowed to move a tower if he owns the majority of the bricks, even if the is not the owner.
        """
        from itertools import permutations
        from_pos = (0, 0)
        to_pos = (0, 1)
        player1 = 1
        some_other_player = 2  # not relevant for this test
        self.assertNotEqual(player1, some_other_player, "misconfigured test: both player IDs should be different")

        # multiple tests with shuffled structure while a clear majority of player1 is maintained
        for structure in permutations([player1] * 2 + [some_other_player]):
            tower = Tower(structure=structure)
            gf = GameField.setup_field({
                from_pos: tower,
                to_pos: Tower(owner=some_other_player)
            })
            rs = MajorityRuleSet(gf)
            with self.subTest(f"explicit: test tower {tower}"):
                self.assertTrue(rs.allows_move(player1, from_pos, to_pos),
                                f"player {player1} should be able to move the tower {tower}")
                self.assertFalse(rs.allows_move(some_other_player, from_pos, to_pos),
                                 f"player {some_other_player} should not be able to move the tower {tower}")
            with self.subTest(f"move: test tower {tower}"):
                self.assertTrue(rs.allows_move(player1, move=Move(from_pos, to_pos)),
                                f"player {player1} should be able to move the tower {tower}")
                self.assertFalse(rs.allows_move(some_other_player, move=Move(from_pos, to_pos)),
                                 f"player {some_other_player} should not be able to move the tower {tower}")

    def test_does_not_allow_move_with_same_owners(self) -> None:
        """
        The rule set should not allow moving a tower onto another with the same owner.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)
        player1 = gf.player1
        gf.set_tower_at(pos=from_pos, tower=Tower(owner=player1))
        gf.set_tower_at(pos=to_pos, tower=Tower(owner=player1))

        rs = MoveOnOpposingOnlyRuleSet(gf)
        with self.subTest("explicit positions"):
            self.assertFalse(rs.allows_move(player1, from_pos, to_pos),
                             "should not allow move when both owners are equal")
        with self.subTest("move object"):
            self.assertFalse(rs.allows_move(player1, move=Move(from_pos, to_pos)),
                             "should not allow move when both owners are equal")

    def test_does_not_allow_moving_too_far(self) -> None:
        """
        The rule set should not allow moving a tower more than one tile (either horizontally, vertically or
        diagonally).
        """
        from_pos = (2, 2)
        positions = [(x, y) for x in [0, 2, 4] for y in [0, 2, 4, 5, 6]]
        for RuleSet in [BaseRuleSet, KingsRuleSet, MajorityRuleSet, MoveOnOpposingOnlyRuleSet]:
            for to_pos in positions:
                gf = GameField(5, 7)
                player1 = gf.player1
                gf.set_tower_at(pos=from_pos, tower=Tower(owner=player1))
                gf.set_tower_at(pos=to_pos, tower=Tower(owner=player1))

                rs = RuleSet(gf)
                with self.subTest(f"explicit: {from_pos} -> {to_pos} in {RuleSet.__name__}"):
                    self.assertFalse(rs.allows_move(player1, from_pos, to_pos),
                                     f"should not allow move from {from_pos} -> {to_pos} (too far)")
                with self.subTest(f"move: {from_pos} -> {to_pos} in {RuleSet.__name__}"):
                    self.assertFalse(rs.allows_move(player1, move=Move(from_pos, to_pos)),
                                     f"should not allow move from {from_pos} -> {to_pos} (too far)")

    def test_does_not_allow_moving_for_wrong_player(self) -> None:
        """
        The rule set should not allow making a move with a tower that the player is not allowed to move at all.
        """
        # TODO review this test case
        from_pos = (1, 1)
        # all fields around from_pos
        positions = [(x, y) for x in [0, 1, 2] for y in [0, 1, 2] if not (x, y) == from_pos]
        for to_pos in positions:
            gf = GameField(3, 3)
            player1 = gf.player1
            player2 = gf.player2
            gf.set_tower_at(pos=from_pos, tower=Tower(structure=[player1, player2, player2]))  # p1 cannot move
            gf.set_tower_at(pos=to_pos, tower=Tower(owner=player2))
            rs = MajorityRuleSet(gf)
            with self.subTest(f"explicit: {from_pos} -> {to_pos}"):
                self.assertFalse(rs.allows_move(player1, from_pos, to_pos),
                                 f"should not allow move from {from_pos} -> {to_pos} (player may not move tower)")
            with self.subTest(f"move: {from_pos} -> {to_pos}"):
                self.assertFalse(rs.allows_move(player1, move=Move(from_pos, to_pos)),
                                 f"should not allow move from {from_pos} -> {to_pos} (player may not move tower)")

    def test_move_with_missing_position_data_raises_error(self) -> None:
        """
        Trying to make a move without providing position data (either with explicit positions or moves) should raise an
        error.
        """
        gf = GameField(1, 2)

        for RuleSet in [BaseRuleSet, KingsRuleSet, MajorityRuleSet, FreeRuleSet, MoveOnOpposingOnlyRuleSet]:
            rs = RuleSet(gf)
            with self.subTest(f"explicit: {RuleSet.__name__}"):
                with self.assertRaises(ValueError):
                    rs.allows_move(player=1)  # player id is irrelevant here

    def test_move_with_missing_explicit_position_data_raises_error(self) -> None:
        """
        Trying to make a move without providing a move object but with only one explicit position should raise an error.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)

        for RuleSet in [BaseRuleSet, KingsRuleSet, MajorityRuleSet, FreeRuleSet, MoveOnOpposingOnlyRuleSet]:
            rs = RuleSet(gf)
            with self.subTest(f"{RuleSet.__name__}"):
                with self.assertRaises(ValueError):
                    rs.allows_move(player=1, from_pos=from_pos, to_pos=None)  # player id is irrelevant here

                with self.assertRaises(ValueError):
                    rs.allows_move(player=1, from_pos=None, to_pos=to_pos)  # player id is irrelevant here
