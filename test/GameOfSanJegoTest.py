import unittest
from unittest import TestCase

from src.GameOfSanJego import Tower

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


if __name__ == "__main__":
    import sys

    while "unsafe" in sys.argv:
        UNSAFE_MODE = True
        sys.argv.remove("unsafe")
    if UNSAFE_MODE:
        print("Warning: Running in UNSAFE_MODE. eval() expressions may be executed")

    unittest.main()
