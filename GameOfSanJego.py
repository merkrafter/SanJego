from typing import Collection


class Tower(object):
    """
    This class serves as a container to hold important information on the game's tokens.
    Towers consist of bricks in different colors (associated with the game's players).
    Each tower as an owner that is determined by the topmost brick.
    """

    def __init__(self, owner: int, structure: Collection[int] = None):
        """
        Creates a new Tower based on the owner and an optional structure (for debugging purposes mainly).
        If no `structure` is given, a new Tower of height one with one brick (the owner) is created.
        :param owner: the player that gets points for this tower
        :param structure: a list of numbers that belong to the game's players
        """
        self.owner = owner
        if structure is None:
            self.structure = [owner]
        else:
            self.structure = structure

    def move_on_top_of(self, tower: 'Tower') -> None:
        """
        Adds the given tower below *this* instance. This method does not change the other `tower` instance nor does it
        check whether the move is actually allowed with the current game's rules..
        :param tower: the Tower to add below *this* one
        """
        self.structure += tower.structure

    @property
    def height(self) -> int:
        """
        The height of a tower is the size of the underlying brick structure and therefore a positive integer.
        :return: height of this tower
        """
        return len(self.structure)

    def __eq__(self, other: 'Tower') -> bool:
        """
        Compares this tower with `other` from a logical point of view. That is, two towers are logically equal, if they
        have the same owner and both `structure`s are equal.
        Note that the behavior therefore depends (partially) on the type of the underlying `structure`.
        :param other: `Tower` instance to compare `self` with
        :return: whether both towers are logically equal
        """
        return hasattr(other, "owner") and other.owner == self.owner and \
               hasattr(other, "structure") and other.structure == self.structure

    def __repr__(self) -> str:
        """
        Returns a string representation that is evaluable to a `Tower` instance, that is, it satisfies
        `eval(t.__repr__())==t`
        for any `Tower` instance `t`.
        :return: a string representation of this tower
        """
        return f"Tower({self.owner}, {self.structure})"

    def __str__(self) -> str:
        """
        Returns a human-readable string representation of this tower.
        In contrast to `__repr__` it does not print the owner explicitly as it is inferable by the topmost brick.
        :return: a human-readable string representation of this tower
        """
        return f"{self.structure}"
