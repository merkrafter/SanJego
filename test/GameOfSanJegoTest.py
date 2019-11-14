import unittest
from unittest import TestCase

from src.GameOfSanJego import Tower, GameField

UNSAFE_MODE = False  # allows the execution of tests that contain eval expressions


class TestTower(TestCase):
    def test__init__with_conflicting_args_raises_error(self) -> None:
        """
        Trying to create a tower with conflicting arguments (owner != structure[0]) should raise an `ValueError` to
        help finding bugs.
        """
        with self.assertRaises(ValueError):
            Tower(1, [2])
            Tower(1, [2, 1])

    def test__init__no_args_raises_error(self) -> None:
        """
        Trying to create a tower without arguments should raise an `ValueError` because it it not clear what to do.
        """
        with self.assertRaises(ValueError):
            Tower()

    def test_can_omit_owner_in__init__(self) -> None:
        """
        The `owner` argument in __init__ may be omitted. The owner is derived from the passed `structure`.
        """
        structure = [2, 1]
        tower = Tower(structure=structure)
        expected_owner = structure[0]
        actual_owner = tower.owner
        self.assertEqual(expected_owner, actual_owner, f"owner should be derived from topmost brick if omitted in\
                                                        constructor")

    def test_height_of_unit_tower(self) -> None:
        """
        The unit tower (with `structure==[]`) should have height 0.
        """
        tower = Tower(structure=[])
        expected_height = 0
        actual_height = tower.height
        self.assertEqual(expected_height, actual_height, f"height of unit tower should be 0 but is {actual_height}")

    def test_height_of_empty_tower(self) -> None:
        """
        Trying to get the height of an empty tower (with `structure is None`) should raise an error to help finding
        bugs in the algorithms.
        """
        tower = Tower(owner=-1)
        tower.structure = None
        with self.assertRaises(AttributeError):
            tower.height

    def test_owner_of_unit_tower(self) -> None:
        """
        Trying to get the owner of a unit tower should raise an error to help finding bugs in the algorithms.
        """
        tower = Tower(structure=[])
        with self.assertRaises(AttributeError):
            tower.owner

    def test_owner_of_empty_tower(self) -> None:
        """
        Trying to get the owner of an empty tower should raise an error to help finding bugs in the algorithms.
        """
        tower = Tower(structure=[])
        tower.structure = None
        with self.assertRaises(AttributeError):
            tower.owner

    def test_default_constructor(self) -> None:
        """
        The default constructor should create a tower with only one brick (the owner)
        """
        owner = 1
        tower = Tower(owner=owner)
        expected_height = 1
        actual_height = tower.height
        self.assertEqual(expected_height, actual_height,
                         f"height of tower created by default constructor \
                         should be {expected_height} but is {actual_height}")

        expected_brick = owner
        actual_brick = tower.structure[0]
        self.assertEqual(expected_brick, actual_brick,
                         f"topmost brick of tower created by default constructor\
                         should be equal to the owner ({expected_brick}) but is {actual_brick}")

    def test_owner_is_topmost_brick(self) -> None:
        """
        The owner of a tower should be equal to the topmost brick (even if that brick is changed later).
        """
        owner = 1
        other_owner = 2
        self.assertNotEqual(owner, other_owner, "misconfigured test: owners should be different")

        tower = Tower(owner=owner)
        tower.structure[0] = other_owner
        expected_owner = other_owner
        actual_owner = tower.owner
        self.assertEqual(expected_owner, actual_owner,
                         f"owner of tower ({actual_owner}) should be equal to the topmost brick ({other_owner})")

    def test_height_after_moving(self) -> None:
        """
        After moving one tower on top of another, the resulting tower's height should be the sum of the initial towers.
        """
        top_owner = 1
        lower_owner = 2
        for top_structure in [None, [top_owner], [top_owner, lower_owner]]:
            for lower_structure in [None, [lower_owner], [lower_owner, lower_owner]]:
                with self.subTest():
                    top_tower = Tower(owner=top_owner, structure=top_structure)
                    lower_tower = Tower(owner=lower_owner, structure=lower_structure)

                    expected_height = top_tower.height + lower_tower.height
                    top_tower.move_on_top_of(lower_tower)
                    actual_height = top_tower.height
                    self.assertEqual(expected_height, actual_height,
                                     f"stacked tower's height should be \
                                     the sum of heights of initial towers ({expected_height}) but is {actual_height}")

    def test_move_on_top_of_None_raises_exception(self) -> None:
        """
        Passing `None` as an argument to `Tower.move_on_top_of` should raise an `ValueError` to help finding
        bugs in the algorithms.
        """
        t = Tower(1)
        with self.assertRaises(ValueError, msg="moving a tower on top of None should raise a ValueError"):
            t.move_on_top_of(None)

    def test_move_empty_towers_raises_exception(self) -> None:
        """
        Calling `Tower.move_on_top_of` on an empty tower or with an empty tower as the argument should raise an
        `ValueError` to help finding bugs in the algorithms.
        """
        tower1 = Tower(1)
        tower2 = Tower(2)
        tower2.structure = None
        with self.assertRaises(ValueError, msg="moving a tower on top of an empty tower should raise a ValueError"):
            tower1.move_on_top_of(tower2)

        with self.assertRaises(ValueError, msg="moving a tower on top of an empty tower should raise a ValueError"):
            tower2.move_on_top_of(tower1)

    def test__eq__for_logically_equal_towers(self) -> None:
        """
        Two towers should be logically equal if they have the same structure, even if they are different instances.
        """
        tower1 = Tower(1)
        tower2 = Tower(1)
        self.assertFalse(tower1 is tower2, "misconfigured test: both towers should be different instances")
        self.assertEqual(tower1, tower2, "both towers should be considered equal")

    def test__eq__for_logically_different_towers(self) -> None:
        """
        Two towers should not be equal if they have a different structure.
        """
        tower1 = Tower(1)
        for structure in [None, [2], [1, 2], [2, 1]]:
            owner = structure[0] if structure is not None else 0
            tower2 = Tower(owner=owner, structure=structure)
            self.assertNotEqual(tower1, tower2, "both towers should not be considered equal")

    def test__eq__with_None(self) -> None:
        """
        A tower should not be equal to None.
        """
        tower = Tower(1)
        self.assertNotEqual(tower, None, "a tower should not be equal to None")

    @unittest.skipUnless(UNSAFE_MODE, "test__repr__ (unsafe test using eval())")
    def test__repr__(self) -> None:
        """
        The evaluation of a tower's __repr__() method should be equal to that tower.
        """
        tower = Tower(1)
        self.assertEqual(eval(tower.__repr__()), tower, "The evaluation of a tower's __repr__() method should be equal\
                                                        to that tower.")


class TestGameField(TestCase):
    def test_default__init__(self) -> None:
        """
        The `GameField` constructor should set the field's height and width correctly.
        """
        for expected_height in range(-10, 11):
            for expected_width in range(-10, 11):
                with self.subTest(f"height {expected_height} and width {expected_width}"):
                    gf = GameField(height=expected_height, width=expected_width)
                    actual_height = gf.height
                    actual_width = gf.width
                    self.assertEqual(expected_height, actual_height,
                                     f"expected given height ({expected_height}) after constructor call\
                                     but got {actual_height}")
                    self.assertEqual(expected_width, actual_width,
                                     f"expected given width ({expected_width}) after constructor call\
                                     but got {actual_width}")

    def test_players_at__init__(self) -> None:
        """
        The `GameField` constructor should set the field's players correctly.
        """
        # make sure to include positive, negative and neutral numbers
        for expected_player1 in range(-1, 2):
            for expected_player2 in [p for p in range(-1, 2) if p != expected_player1]:
                with self.subTest(f"max. player {expected_player1} and min. player {expected_player2}"):
                    gf = GameField(height=2, width=2, player1=expected_player1, player2=expected_player2)
                    actual_player1 = gf.player1
                    actual_player2 = gf.player2
                    self.assertEqual(expected_player1, actual_player1,
                                     f"expected given player1 ({expected_player1}) after constructor call\
                                     but got {actual_player1}")
                    self.assertEqual(expected_player2, actual_player2,
                                     f"expected given player2 ({expected_player2}) after constructor call\
                                 but got {actual_player2}")

    def test_players_at__init__are_equal(self) -> None:
        """
        Trying to initialize a game with two identical players should raise an Error to help finding bugs in the code.
        """
        player_id = 1
        some_size = (2, 2)  # does not play a role for this test
        with self.assertRaises(ValueError):
            GameField(*some_size, player1=player_id, player2=player_id)

    def test_players_on_field(self) -> None:
        """
        The `GameField`'s board should contain (and *only* contain) the players specified at the constructor call.
        """
        # make sure to include positive, negative and neutral numbers
        for expected_player1 in range(-1, 2):
            for expected_player2 in [p for p in range(-1, 2) if p != expected_player1]:
                with self.subTest(f"players {expected_player1} and {expected_player2}"):
                    gf = GameField(height=2, width=2, player1=expected_player1, player2=expected_player2)

                    # check whether the intended players have towers on the board
                    self.assertTrue(expected_player1 in map(lambda x: x.owner, gf.field),
                                    f"player {expected_player1} should be on the board")
                    self.assertTrue(expected_player2 in map(lambda x: x.owner, gf.field),
                                    f"player {expected_player2} should be on the board")

                    # check whether there are towers with other owners than the given players on the board
                    additional_players_on_board = [p for p in map(lambda x: x.owner, gf.field) if
                                                   p != expected_player1 and p != expected_player2]
                    self.assertEqual([], additional_players_on_board,
                                     f"there should be no more players on the board than {expected_player1} and\
                                    {expected_player2} but found {additional_players_on_board}")

    def test_value_after_construction(self) -> None:
        """
        Right after creation, a game field's value should be 0 to make the game fair.
        """
        expected_value = 0
        for height in range(1, 10):
            for width in range(1, 10):
                if not height * width == 1:  # if there's only one tower, the game value is not 0
                    with self.subTest(f"height {height} and {width}"):
                        gf = GameField(height=height, width=width)
                        actual_value = gf.value
                        self.assertEqual(expected_value, actual_value,
                                         "the value of a GameField should be 0 after creation")

    def test_value_after_construction_with_one_tower(self) -> None:
        """
        If there is only one tower on the field, the game value should be `±height` of that tower.
        """

        gf = GameField(1, 1)
        for tower_height in range(1, 6):
            # maximising player
            with self.subTest(f"height {tower_height} for max"):
                gf.set_tower_at(pos=(0, 0), tower=Tower(structure=[gf.player1] * tower_height))
                expected_value = tower_height
                actual_value = gf.value
                self.assertEqual(expected_value, actual_value, f"one tower with height {expected_value} owned by max\
                                 player should give a game value of {expected_value} but is {actual_value}")

            # minimising player
            with self.subTest(f"height {tower_height} for min"):
                gf.set_tower_at(pos=(0, 0), tower=Tower(structure=[gf.player2] * tower_height))
                expected_value = -1 * tower_height
                actual_value = gf.value
                self.assertEqual(expected_value, actual_value, f"one tower with height {expected_value} owned by min\
                                 player should give a game value of {expected_value} but is {actual_value}")

    def test_value_after_first_move(self) -> None:
        """
        After making the first move, a game field's value should be ±1 for non-trivial fields depending on the player
        making the move.
        A trivial field is one of size `height * width <= 2`
        """

        height = 2
        width = 3

        self.assertTrue(height * width > 2,
                        f"misconfigured test: height*width should be greater than 2 but is {height}*{width} <= 2")

        with self.subTest("move for max (1st) player"):
            gf = GameField(height=height, width=width)
            gf.make_move((0, 0), (0, 1))  # move in favor of player 1 (maximising)
            expected_value = 1
            actual_value = gf.value
            self.assertEqual(expected_value, actual_value,
                             "the value of a GameField should be 1 after first move of maximising (1st) player")

        with self.subTest("move for min (2nd) player"):
            gf = GameField(height=height, width=width)
            gf.make_move((0, 1), (0, 0))  # move in favor of player 2 (minimising)
            expected_value = -1
            actual_value = gf.value
            self.assertEqual(expected_value, actual_value,
                             "the value of a GameField should be -1 after first move of minimising (2nd) player")

    def test_set_and_get_tower_at(self) -> None:
        """
        Setting and getting a tower to and from the same position should return that tower.
        """
        pos = (0, 0)
        gf = GameField(1, 1)
        expected_tower = Tower(owner=gf.player1)
        gf.set_tower_at(pos, expected_tower)
        actual_tower = gf.get_tower_at(pos)
        self.assertEqual(expected_tower, actual_tower,
                         f"Setting a tower to a location and getting one from there right after setting should return\
                         the same tower")

    def test_get_tower_at_invalid_positions(self) -> None:
        """
        Getting a tower from an invalid position should not raise an error but return `None` instead to simplify
        algorithms later.
        """
        height = 5
        width = 4
        for x in [-1, 0, height]:
            for y in [-1, 0, width]:
                if not (x == 0 and y == 0):  # this is a valid position
                    with self.subTest(f"pos = ({x}, {y})"):
                        expected_tower = None
                        gf = GameField(height=height, width=width)
                        actual_tower = gf.get_tower_at((x, y))
                        self.assertEqual(expected_tower, actual_tower,
                                         "Getting a tower from an invalid position should return None")

    def test_set_tower_at_valid_positions(self) -> None:
        """
        Setting a tower at a valid position should communicate that this operation was successful.
        """
        height = 5
        width = 4
        some_tower = Tower(owner=1)  # not relevant for this test

        # these for loops cover the edge cases and the one in the middle
        for x in [0, height // 2, height - 1]:
            for y in [0, height // 2, width - 1]:
                with self.subTest(f"pos = ({x}, {y})"):
                    gf = GameField(height=height, width=width)
                    self.assertTrue(gf.set_tower_at(pos=(x, y), tower=some_tower),
                                    "Setting a tower to a valid position should return True")

    def test_set_tower_at_invalid_positions(self) -> None:
        """
        Setting a tower at an invalid position should communicate that this operation could not be fulfilled.
        """
        height = 5
        width = 4
        some_tower = Tower(owner=1)  # not relevant for this test

        # these loops test positions that are just one off as well as positions that are far off
        for x in [-5, -1, 0, height]:
            for y in [-1, 0, width]:
                if not (x == 0 and y == 0):  # this is a valid position
                    with self.subTest(f"pos = ({x}, {y})"):
                        gf = GameField(height=height, width=width)
                        self.assertFalse(gf.set_tower_at(pos=(x, y), tower=some_tower),
                                         "Setting a tower to an invalid position should return False")

    def test_make_move(self) -> None:
        """
        Making a valid move should communicate that this operation was successful.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)

        successful: bool = gf.make_move(from_pos, to_pos)
        self.assertTrue(successful, "Making a valid move should return True")

    def test_make_move_to_and_from_invalid_positions(self) -> None:
        """
        Making an invalid move should communicate that this operation was not successful.
        """
        height = 5
        width = 4
        positions = [(x, y) for x in [-1, 0, height] for y in [-1, 0, width] if not (x == 0 and y == 0)]
        for from_pos in positions:
            for to_pos in positions:
                with self.subTest(f"{from_pos} -> {to_pos}"):
                    gf = GameField(height=height, width=width)

                    successful: bool = gf.make_move(from_pos, to_pos)
                    self.assertFalse(successful, "Making an invalid move should return False")

    def test_make_move_inplace(self) -> None:
        """
        It should not be possible to move a tower to its own position.
        """
        pos = (0, 0)
        gf = GameField(1, 2)

        successful: bool = gf.make_move(from_pos=pos, to_pos=pos)
        self.assertFalse(successful, "Trying to move a tower from and to the same position should return False")

    def test_moves_towers_correctly(self) -> None:
        """
        Moving a tower should remove a tower from the 'source' position and set a combined tower at the target position.
        It is free for the implementation whether "remove" means setting to `None` or just insert a unit tower of
        height 0.
        """
        player1 = 1
        player2 = 2
        top_tower = Tower(structure=[player1])
        lower_tower = Tower(structure=[player2])
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2, player1=player1, player2=player2)
        gf.set_tower_at(from_pos, top_tower)
        gf.set_tower_at(to_pos, lower_tower)

        gf.make_move(from_pos, to_pos)

        # check source position
        tower_at_from_pos = gf.get_tower_at(from_pos)
        self.assertTrue(tower_at_from_pos is None or tower_at_from_pos.height == 0,
                        f"the source position {from_pos} should contain an empty or unit tower after move\
                        but found {tower_at_from_pos}")

        # check target position
        expected_tower = Tower(structure=[player1, player2])
        actual_tower = gf.get_tower_at(to_pos)
        self.assertEqual(expected_tower, actual_tower, f"Expected combined tower ({expected_tower}) at {to_pos} after\
                         move but found {actual_tower}")

    def test__eq__(self) -> None:
        """
        Two game fields should be compared semantically, that is, be equal if all of their towers are equal.
        There is no need for identity.
        """
        gf1 = GameField.setup_field({
            (0, 0): Tower(owner=0),
            (1, 1): Tower(owner=1)
        })
        gf2 = GameField.setup_field({
            (0, 0): Tower(owner=0),
            (1, 1): Tower(owner=1)
        })
        self.assertEqual(gf1, gf2, "both game fields should be considered equal")

    def test_not__eq__(self) -> None:
        """
        Two game fields should not be considered equal if their towers differ.
        """
        gf1 = GameField.setup_field({
            (0, 0): Tower(owner=0),
            (1, 1): Tower(owner=1)
        })
        gf2 = GameField.setup_field({
            (0, 0): Tower(owner=0),
        })
        self.assertNotEqual(gf1, gf2, "both game fields should not be considered equal")


if __name__ == "__main__":
    import sys

    while "unsafe" in sys.argv:
        UNSAFE_MODE = True
        sys.argv.remove("unsafe")
    if UNSAFE_MODE:
        print("Warning: Running in UNSAFE_MODE. eval() expressions may be executed")

    unittest.main()
