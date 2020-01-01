import unittest
from unittest import TestCase

from src.GameOfSanJego import Tower, GameField, Move

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

    def test_attaching(self) -> None:
        """
        After attaching one tower to another, the resulting tower's structure should be equal to the combined structure
        of the former towers.
        """
        lower_structure = [0]
        upper_structure = [1]
        expected_structure = upper_structure + lower_structure  # left in list <=> top of tower
        lower_tower = Tower(structure=lower_structure)
        upper_tower = Tower(structure=upper_structure)

        lower_tower.attach(upper_tower)

        self.assertEqual(expected_structure, lower_tower.structure,
                         f"after attaching {upper_tower} on top of {lower_tower},\
                         the resulting tower should have the combined structure")

    def test_height_after_attaching(self) -> None:
        """
        After attaching one tower to another, the resulting tower's height should be the sum of the initial towers.
        """
        top_owner = 1
        lower_owner = 2
        for top_structure in [None, [top_owner], [top_owner, lower_owner]]:
            for lower_structure in [None, [lower_owner], [lower_owner, lower_owner]]:
                with self.subTest():
                    top_tower = Tower(owner=top_owner, structure=top_structure)
                    lower_tower = Tower(owner=lower_owner, structure=lower_structure)

                    expected_height = top_tower.height + lower_tower.height
                    lower_tower.attach(top_tower)
                    actual_height = lower_tower.height
                    self.assertEqual(expected_height, actual_height,
                                     f"stacked tower's height should be \
                                     the sum of heights of initial towers ({expected_height}) but is {actual_height}")

    def test_attach_None_raises_exception(self) -> None:
        """
        Passing `None` as an argument to `Tower.attach` should raise a `ValueError` to help finding
        bugs in the algorithms.
        """
        t = Tower(1)
        with self.assertRaises(ValueError, msg="attaching None to a tower should raise a ValueError"):
            t.attach(None)

    def test_attach_empty_towers_raises_exception(self) -> None:
        """
        Calling `Tower.attach` on an empty tower or with an empty tower as the argument should raise a
        `ValueError` to help finding bugs in the algorithms.
        """
        tower = Tower(1)
        empty_tower = Tower(2)
        empty_tower.structure = None
        with self.assertRaises(ValueError, msg="attaching an empty tower should raise a ValueError"):
            tower.attach(empty_tower)

        with self.assertRaises(ValueError, msg="attaching a tower to an empty tower should raise a ValueError"):
            empty_tower.attach(tower)

    def test_detach_topmost_brick(self) -> None:
        """
        A tower should be able to detach its (existing) topmost brick.
        """
        expected_structure = [2, 1]
        topmost_brick = [1]
        tower_under_test = Tower(structure=topmost_brick + expected_structure)
        tower_under_test.detach(Tower(structure=topmost_brick))
        expected_tower = Tower(structure=expected_structure)
        self.assertEqual(expected_tower, tower_under_test)

    def test_detach_non_existing_brick(self) -> None:
        """
        A tower should raise an error when trying to detach its non-existing topmost brick.
        """
        with self.assertRaises(ValueError):
            tower_under_test = Tower(structure=[1, 2, 1])
            tower_under_test.detach(Tower(structure=[2]))  # not the topmost brick

    def test_detach_None(self) -> None:
        """
        A tower should raise an error when trying to detach `None`.
        """
        with self.assertRaises(ValueError):
            tower_under_test = Tower(structure=[1, 2, 1])
            tower_under_test.detach(None)

    def test_detach_empty(self) -> None:
        """
        When trying to remove an empty tower, nothing should happen.
        """
        expected_structure = [2, 1]
        tower_under_test = Tower(structure=expected_structure)
        tower_to_detach = Tower(1)
        tower_to_detach.structure = []  # make the tower empty
        tower_under_test.detach(tower_to_detach)
        expected_tower = Tower(structure=expected_structure)
        self.assertEqual(expected_tower, tower_under_test)

    def test_attach_and_detach(self) -> None:
        """
        After attaching and detaching a tower to/from another, the lower tower should be the same in the end.
        """
        expected_structure = [1, 2, 1]
        upper_tower = Tower(structure=[2, 1, 2])
        lower_tower = Tower(structure=expected_structure)

        lower_tower.attach(upper_tower)
        lower_tower.detach(upper_tower)

        expected_tower = Tower(structure=expected_structure)
        self.assertEqual(expected_tower, lower_tower)

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


class MoveTest(TestCase):
    def test_new_move_has_not_been_made(self) -> None:
        """
        A newly created move should not indicate it has been made already.
        """
        from_pos = (0, 0)  # values irrelevant
        to_pos = (0, 1)  # values irrelevant
        move = Move(from_pos, to_pos)
        self.assertFalse(move.already_made(), "newly created move should not indicate it has been made already")

    def test_skipping_move_creation(self) -> None:
        """
        The construction method for skipping moves should work together with `is_skipping_move`.
        """
        move = Move.skip()
        self.assertTrue(move.is_skip_move(), "Creation of a skipping move should actually create one")

    def test_make_move_sets_affected_tower(self) -> None:
        """
        Making a move should set the moved tower so that the move can be reversed.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        from_tower = Tower(structure=[0, 1])
        from_tower_expected = Tower(structure=[0, 1])
        to_tower = Tower(1)
        gf = GameField.setup_field({
            from_pos: from_tower,
            to_pos: to_tower
        })

        move = Move(from_pos, to_pos)

        gf.make_move(move=move)
        self.assertTrue(move.already_made(), "A move should recognize it has been made")
        self.assertEqual(move.from_tower, from_tower_expected, "Moved tower should be stored in move object")

    def test_making_two_moves_sets_tower_correctly(self) -> None:
        """
        Make two consecutive moves with the same tower. After that, the Move object for the first move should not have a
        changed from_tower attribute, preventing the use of a reference in the Move object that can be modified later.
        """
        move1 = Move(from_pos=(0, 0), to_pos=(0, 1))
        move2 = Move(from_pos=(0, 1), to_pos=(0, 2))
        self.assertEqual(move1.to_pos, move2.from_pos, "Misconfigured test: moves should be connected")

        tower1 = Tower(structure=[0, 1])
        tower2 = Tower(structure=[1, 1])
        tower3 = Tower(structure=[1, 0, 1])

        expected_from_tower = Tower(structure=[0, 1])
        self.assertEqual(expected_from_tower, tower1, "Misconfigured test: expected tower must be equal to first tower")

        gf = GameField.setup_field({
            move1.from_pos: tower1,
            move1.to_pos: tower2,
            move2.to_pos: tower3
        })

        gf.make_move(move=move1)
        gf.make_move(move=move2)
        self.assertEqual(move1.from_tower, expected_from_tower, "First move should store first moved tower")


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
                    # TODO avoid accessing gf.field directly
                    self.assertTrue(expected_player1 in map(lambda x: x.owner, gf.field.values()),
                                    f"player {expected_player1} should be on the board")
                    self.assertTrue(expected_player2 in map(lambda x: x.owner, gf.field.values()),
                                    f"player {expected_player2} should be on the board")

                    # check whether there are towers with other owners than the given players on the board
                    additional_players_on_board = [p for p in map(lambda x: x.owner, gf.field.values()) if
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

    def test_make_move_with_explicit_positions(self) -> None:
        """
        Making a valid move should communicate that this operation was successful.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)

        successful: bool = gf.make_move(from_pos, to_pos)
        self.assertTrue(successful, "Making a valid move should return True")

    def test_prohibit_making_move_twice(self) -> None:
        """
        Making the same move that has been made already should raise an error.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)

        move = Move(from_pos, to_pos)
        move.from_tower = Tower(1)  # value does not matter here

        with self.assertRaises(RuntimeError):
            gf.make_move(move=move)

    def test_making_skip_move(self) -> None:
        """
        Making a skip move should do nothing.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)
        expected_gf = GameField(1, 2)

        move = Move.skip()

        gf.make_move(move=move)
        self.assertEqual(expected_gf.get_tower_at(from_pos), gf.get_tower_at(from_pos),
                         "Making a skip move should not change the game field")
        self.assertEqual(expected_gf.get_tower_at(to_pos), gf.get_tower_at(to_pos),
                         "Making a skip move should not change the game field")
        self.assertIsNone(move.from_tower, "Making a skip move should not set the moved tower")

    def test_making_skip_move_returns_true(self) -> None:
        """
        Making a skip move should return true, indicating success.
        """
        gf = GameField(1, 2)
        self.assertTrue(gf.make_move(move=Move.skip()), "Making a skip move should return true, indicating success")

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

    def test_moves_towers_correctly_with_explicit_positions(self) -> None:
        """
        Moving a tower should remove a tower from the 'source' position and set a combined tower at the target position.
        It is free for the implementation whether "remove" means setting to `None` or just insert a unit tower of
        height 0.
        This test case uses explicit positions instead of a Move object.
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

    def test_moves_towers_correctly_with_move_object(self) -> None:
        """
        Moving a tower should remove a tower from the 'source' position and set a combined tower at the target position.
        It is free for the implementation whether "remove" means setting to `None` or just insert a unit tower of
        height 0.
        This test case uses a Move object instead of explicit positions.
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

        move = Move(from_pos, to_pos)

        gf.make_move(move=move)

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

    def test_move_without_position_data_raises_error(self) -> None:
        """
        Trying to make a move without providing position data (either with explicit positions or moves) should raise an
        error.
        """
        gf = GameField(1, 2)

        with self.assertRaises(ValueError):
            gf.make_move()

    def test_move_with_missing_explicit_position_data_raises_error(self) -> None:
        """
        Trying to make a move without providing a move object but with only one explicit position should raise an error.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)

        with self.assertRaises(ValueError):
            gf.make_move(from_pos=from_pos, to_pos=None)

        with self.assertRaises(ValueError):
            gf.make_move(from_pos=None, to_pos=to_pos)

    def test_move_object_has_precedence_over_explicit_positions(self) -> None:
        """
        If both a move and explicit positions are given to GameField.make_move, the move object's positions should be
        the ones used.
        """
        upper_tower_id = 1
        lower_tower_id = 2

        # idea:
        # [1] [ ]
        # [2] [ ]
        # after the move, [2] should be moved while [1] should still be at (0,0)
        # NOTE THAT it is not possible to move towers to empty spots, hence artificial towers are inserted
        # at (0,1) and (1,1)
        from_pos_explicit = (0, 0)
        to_pos_explicit = (0, 1)
        from_pos_move = (1, 0)
        to_pos_move = (1, 1)

        gf = GameField.setup_field({
            from_pos_explicit: Tower(upper_tower_id),
            from_pos_move: Tower(lower_tower_id),

            # irrelevant; only here because towers can only be moved on top of others
            to_pos_explicit: Tower(1),
            to_pos_move: Tower(1)
        })

        move = Move(from_pos_move, to_pos_move)
        gf.make_move(from_pos=from_pos_explicit, to_pos=to_pos_explicit, move=move)

        # check whether the upper tower was NOT moved
        self.assertEqual(upper_tower_id, gf.get_tower_at(from_pos_explicit).owner,
                         "explicitly specified tower should not be moved when move object was given")
        self.assertEqual(1, gf.get_tower_at(to_pos_explicit).height,
                         "explicitly specified tower should not be moved when move object was given")

        # check whether the lower tower WAS moved
        self.assertTrue(gf.get_tower_at(from_pos_move) is None or gf.get_tower_at(from_pos_move).height == 0,
                        "move-specified tower should be moved when move object was given")
        self.assertEqual(lower_tower_id, gf.get_tower_at(to_pos_move).owner,
                         "move-specified tower should be moved when move object was given")

    def test_take_back(self) -> None:
        """
        A game field should be able to take back a move.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        from_brick = [2]
        to_brick = [1]

        game_field = GameField.setup_field({to_pos: Tower(structure=from_brick + to_brick)})  # no tower at from_pos
        move = Move(from_pos, to_pos)
        move.from_tower = Tower(structure=from_brick)
        game_field.take_back(move)
        expected_game_field = GameField.setup_field(
            {from_pos: Tower(structure=from_brick), to_pos: Tower(structure=to_brick)})
        self.assertEqual(expected_game_field.get_tower_at(from_pos), game_field.get_tower_at(from_pos))
        self.assertEqual(expected_game_field.get_tower_at(to_pos), game_field.get_tower_at(to_pos))

    def test_take_back_resets_move(self) -> None:
        """
        After the `take_back` method, a move should not be marked as already been made.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        moved_brick = [0]
        game_field = GameField.setup_field({to_pos: Tower(structure=moved_brick + [2])})  # no tower at from_pos
        move = Move(from_pos, to_pos)
        move.from_tower = Tower(structure=moved_brick)

        self.assertTrue(move.already_made())
        game_field.take_back(move)
        self.assertFalse(move.already_made())

    def test_take_back_fails_on_new_move(self) -> None:
        """
        The `take_back` method should not allow taking back a move that has not been made yet.
        """
        game_field = GameField.setup_field({(0, 1): Tower(2)})
        move = Move(from_pos=(0, 0), to_pos=(0, 1))
        self.assertFalse(move.already_made(), "misconfigured test: move should not be marked as already been made")
        with self.assertRaises(ValueError):
            game_field.take_back(move)

    def test_take_back_does_not_allow_tower_at_from_pos(self) -> None:
        """
        The `take_back` method should not allow a tower at `from_pos`; this should be empty.
        """
        game_field = GameField(1, 2)  # from_pos (0,0) has a tower on it
        move = Move(from_pos=(0, 0), to_pos=(0, 1))
        move.from_tower = Tower(2)
        with self.assertRaises(RuntimeError):
            game_field.take_back(move)

    def test_take_back_does_not_allow_None_at_to_pos(self) -> None:
        """
        The `take_back` method should force a tower at `to_pos`.
        """
        game_field = GameField.setup_field({(0, 0): Tower(0)}, min_width=2)  # to_pos (0,1) has no tower on it
        move = Move(from_pos=(0, 0), to_pos=(0, 1))
        move.from_tower = Tower(2)  # exact value does not matter; only makes sure the move counts as been made
        with self.assertRaises(RuntimeError):
            game_field.take_back(move)

    def test_take_back_does_not_allow_wrong_upper_tower(self) -> None:
        """
        The `take_back` method should not allow taking back an `upper_tower` that is not *actually* on top.
        """
        game_field = GameField.setup_field({(0, 1): Tower(2)})  # from_pos (0,0) has no tower on it
        move = Move(from_pos=(0, 0), to_pos=(0, 1))
        move.from_tower = Tower(1)  # not on top of the tower at (0,1)
        with self.assertRaises(ValueError):
            game_field.take_back(move)

    def test_take_back_does_not_allow_taking_back_complete_tower(self) -> None:
        """
        The `take_back` method should not allow taking back a complete tower as this would imply that the tower was
        moved to an empty square.
        """
        game_field = GameField(1, 2)
        move = Move(from_pos=(0, 0), to_pos=(0, 1))
        move.from_tower = game_field.get_tower_at(move.to_pos)
        with self.assertRaises(RuntimeError):
            game_field.take_back(move)

    def test_take_back_skip_move(self) -> None:
        """
        Taking back a skip move should not do anything.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        gf = GameField(1, 2)
        expected_gf = GameField(1, 2)

        move = Move.skip()

        gf.take_back(move=move)
        self.assertEqual(expected_gf.get_tower_at(from_pos), gf.get_tower_at(from_pos),
                         "Taking back a skip move should not change the game field")
        self.assertEqual(expected_gf.get_tower_at(to_pos), gf.get_tower_at(to_pos),
                         "Taking back a skip move should not change the game field")

    def test_move_and_taking_back(self) -> None:
        """
        After making and then taking back a move, the field should be the same as before.
        """
        from_pos = (0, 0)
        to_pos = (0, 1)
        game_field = GameField(1, 2)
        prev_game_field = GameField(1, 2)  # equal to game_field
        move = Move(from_pos=from_pos, to_pos=to_pos)
        game_field.make_move(move=move)
        game_field.take_back(move)
        self.assertEqual(prev_game_field.get_tower_at(from_pos), game_field.get_tower_at(from_pos))
        self.assertEqual(prev_game_field.get_tower_at(to_pos), game_field.get_tower_at(to_pos))

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
