from typing import Collection, Optional


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


class GameField(object):
    """
    This class is a container for `Tower` instances and provides methods to manipulate them.
    However, it does not contain game logic in terms of rules (i.e. is does not check for allowed moves).
    """

    def __init__(self, height: int, width: int, player1: int = 0, player2: int = 1):
        """
        Creates a new board and initializes the underlying `Tower` structure by placing towers of the two players in a
        chessboard-like pattern.
        :param height: number of rows of the board
        :param width: number of columns of the board
        :param player1: ID of first player
        :param player2: ID of second player
        """
        self.height = height
        self.width = width
        self.player1 = player1
        self.player2 = player2
        # TODO: use correct player ids
        self.field = [Tower((h + w) % 2) for h in range(self.height) for w in range(self.width)]

    @property
    def value(self) -> int:
        """
        The value of a board is determined by the difference in height of the highest towers of both players.
        The returned value is greater than 0 if player 1 has an edge over player 2.
        :return: difference in height of both players' highest towers
        """
        # max(height(tower of that respective player))
        highest_p1 = max(map(lambda tower: tower.height, filter(lambda tower: tower.owner == self.player1, self.field)))
        highest_p2 = max(map(lambda tower: tower.height, filter(lambda tower: tower.owner == self.player2, self.field)))
        return highest_p1 - highest_p2

    def __float__(self) -> float:
        """
        :return: this game field's value as a float
        """
        return float(self.value)

    def __int__(self):
        """
        :return: this game field's value as an int for convenience reasons
        """
        return int(self.value)

    def get_tower_at(self, pos: (int, int)) -> Optional[Tower]:
        """
        Returns the tower at the given position. Can be `None` if either the `pos` is outside the game field or
        there is no tower at the specified position.
        :param pos: specifies the position to get a tower from
        :return: a `Tower` instance, if there is a one at `pos` or `None` otherwise.
        """
        if not 0 <= pos[0] < self.height and 0 <= pos[1] < self.width:
            return None
        x = pos[0]
        y = pos[1]
        return self.field[x * self.width + y]

    def set_tower_at(self, pos: (int, int), tower: Optional[Tower]) -> bool:
        """
        Sets the tower at the specified position, overwrites any other values at that position, and returns whether this
        operation was successful.
        This method is not successful, if `pos` is outside the board.
        :param tower: the tower to set; if `None`, deletes anything at the given position
        :param pos: the 0-indexed position to set the tower at
        :return: whether this method was successful
        """
        if not 0 <= pos[0] < self.height and 0 <= pos[1] < self.width:
            return False
        x = pos[0]
        y = pos[1]
        self.field[x * self.width + y] = tower
        return True

    def make_move(self, from_pos: (int, int), to_pos: (int, int)) -> bool:
        """
        Moves the tower at `from_pos` on top of the tower at `to_pos` and returns whether this was successful.
        The method does not check whether this move is legal under the current rules.
        It does, however, check whether this move is technically possible, i.e. both positions contain towers.
        Both positions are 0-indexed and specify the row in the first component and the column in the second.
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :return: whether the move was successful
        """
        # check whether there are towers on both positions
        top_tower = self.get_tower_at(from_pos)
        lower_tower = self.get_tower_at(to_pos)

        if top_tower is None or lower_tower is None:
            return False

        top_tower.move_on_top_of(lower_tower)  # only adds lower_tower to top_tower in the current implementation
        self.set_tower_at(to_pos, top_tower)
        self.set_tower_at(from_pos, None)
        return True
