from typing import Optional, Sequence, Dict, Tuple


class Tower(object):
    """
    This class serves as a container to hold important information on the game's tokens.
    Towers consist of bricks in different colors (associated with the game's players).
    Each tower as an owner that is determined by the topmost brick.
    """

    def __init__(self, owner: Optional[int] = None, structure: Optional[Sequence[int]] = None):
        """
        Creates a new Tower based on the owner and an optional structure (for debugging purposes mainly).
        If no `structure` is given, a new Tower of height one with one brick (the owner) is created.
        :param owner: the player that gets points for this tower
        :param structure: a list of numbers that belong to the game's players
        """
        if owner is None:
            if structure is None:
                raise ValueError("can not create a tower without any arguments")
            else:
                self.structure = structure
        else:  # owner is passed
            if structure is None:
                self.structure = [owner]
            elif len(structure) > 0 and structure[0] == owner:  # owner and structure passed
                self.structure = structure
            else:  # both passed but conflicting
                raise ValueError(f"passed owner ({owner}) and structure ({structure}) are conflicting")

    @property
    def owner(self) -> int:
        """
        The owner of a tower is derived from the topmost brick.
        It is not defined for empty (`structure is None`) or unit (`structure==[]`) towers hence an `AttributeError`
        is raised in that case.
        :return: ID of the player owning this `Tower`
        """
        if self.structure is None or len(self.structure) == 0:
            raise AttributeError("an empty or unit tower does not have an owner")
        return self.structure[0]

    def move_on_top_of(self, tower: 'Tower') -> None:
        """
        Adds the given tower below *this* instance. This method does not change the other `tower` instance nor does it
        check whether the move is actually allowed with the current game's rules..
        :param tower: the Tower to add below *this* one
        """
        # TODO make this a method of the lower tower and change the GameField method accordingly; new name: attach
        if tower is None:
            raise ValueError("can not move this tower on top of None")
        if self.structure is None or tower.structure is None:
            raise ValueError("can not move empty towers on top of each other")
        self.structure += tower.structure

    def detach(self, tower: 'Tower') -> None:
        """
        Removes the given tower from the top of this (self) tower
        """
        if tower is None:
            raise ValueError("can not detach None from this tower")

        if not self.structure[:len(tower.structure)] == tower.structure:
            raise ValueError(f"{tower} is not on top of {self}")

        del self.structure[:len(tower.structure)]

    @property
    def height(self) -> int:
        """
        The height of a tower is the size of the underlying brick structure and therefore a non-negative integer.
        It is not defined for empty (`structure is None`) towers hence an `AttributeError` is raised in that case.
        :return: height of this tower
        """
        if self.structure is None:
            raise AttributeError("an empty tower does not have a height")
        return len(self.structure)

    def __eq__(self, other: 'Tower') -> bool:
        """
        Compares this tower with `other` from a logical point of view. That is, two towers are logically equal, if they
        have the same owner and both `structure`s are equal.
        Note that the behavior therefore depends (partially) on the type of the underlying `structure`.
        :param other: `Tower` instance to compare `self` with
        :return: whether both towers are logically equal
        """
        return hasattr(other, "structure") and other.structure == self.structure

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


class Move(object):
    """
    This class stores information about one move in a game of San Jego.
    It does not contain much logic in order to keep it simple.
    In addition to the from and to positions, moves store a reference of the moved tower
    after making the move to allow taking a move back.
    """

    def __init__(self, from_pos: (int, int), to_pos: (int, int)) -> None:
        """
        Creates a new Move object by setting the source and target positions
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        """
        self.from_pos = from_pos
        self.to_pos = to_pos
        self.from_tower: Optional[Tower] = None

    def already_made(self) -> bool:
        """
        A move counts as being made when the `from_tower` reference is not `None` anymore.
        :return: whether this move has already been made
        """
        return self.from_tower is not None

    @staticmethod
    def skip() -> "Move":
        """
        This is a convenience method that allows more readable code when creating skipping moves.
        :return: a move that indicates skipping
        """
        return Move(from_pos=(-1, -1), to_pos=(-1, -1))

    def is_skip_move(self) -> bool:
        """
        :return: whether this move is a skipping move
        """
        return self.from_pos == (-1, -1) == self.to_pos

    def __repr__(self) -> str:
        """
        Returns a string representation of this move that can be evaluated to get a Move object back.
        :return: a evaluable string representation of this move
        """
        if self.is_skip_move():
            return "Move.skip()"
        return f"Move({self.from_pos}, {self.to_pos})"

    def __str__(self) -> str:
        """
        Returns a string representation of this move in the format
        "from_pos -> to_pos"
        if this is not a skipping move and an indicator for this being a skipping move else.
        :return: string representation of this move
        """
        if self.is_skip_move():
            return "<skip>"
        return f"{self.from_pos} -> {self.to_pos}"

    def __eq__(self, other: 'Move') -> bool:
        """
        Returns whether the `from_pos` and `to_pos` of self and `other` are equal.
        """
        return hasattr(other, "from_pos") and other.from_pos == self.from_pos and \
               hasattr(other, "to_pos") and other.to_pos == self.to_pos


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
        if player1 == player2:
            raise ValueError(f"a game must be initialized with two distinct players but got {player1} and {player2}")
        self.height = height
        self.width = width
        self.player1 = player1
        self.player2 = player2
        player_tuple = (player1, player2)
        self.field = [Tower(owner=player_tuple[(h + w) % 2]) for h in range(self.height) for w in range(self.width)]

    # TODO make this a method of RuleSet
    @property
    def value(self) -> int:
        """
        The value of a board is determined by the difference in height of the highest towers of both players.
        The returned value is greater than 0 if player 1 has an edge over player 2.
        :return: difference in height of both players' highest towers
        """
        # max(height(tower of that respective player))
        highest_p1 = max(map(lambda tower: tower.height,
                             filter(
                                 lambda tower: tower is not None and tower.height > 0 and tower.owner == self.player1,
                                 self.field)),
                         default=0)
        highest_p2 = max(map(lambda tower: tower.height,
                             filter(
                                 lambda tower: tower is not None and tower.height > 0 and tower.owner == self.player2,
                                 self.field)),
                         default=0)
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

    def __eq__(self, other: 'GameField') -> bool:
        """
        Compares this game field with `other` from a logical point of view. That is, two game fields are logically
        equal, if they have the same underlying `field`, `player1` and `player2` attributes.
        Note that the behavior therefore depends (partially) on the type of the underlying `field`.
        :param other: `GameField` instance to compare `self` with
        :return: whether both game fields are logically equal
        """
        return other.field == self.field and other.player1 == self.player1 and other.player2 == self.player2

    def get_tower_at(self, pos: (int, int)) -> Optional[Tower]:
        """
        Returns the tower at the given position. Can be `None` if either the `pos` is outside the game field or
        there is no tower at the specified position.
        :param pos: specifies the position to get a tower from
        :return: a `Tower` instance, if there is a one at `pos` or `None` otherwise.
        """
        if not (0 <= pos[0] < self.height and 0 <= pos[1] < self.width):
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
        if not (0 <= pos[0] < self.height and 0 <= pos[1] < self.width):
            return False

        # if the position is to be cleared, replace it with a "unit tower" so it does not break the calculation of the
        # game value (as None would)
        if tower is None:
            tower = Tower(structure=[])

        x = pos[0]
        y = pos[1]
        self.field[x * self.width + y] = tower
        return True

    def make_move(self, from_pos: Optional[Tuple[int, int]] = None, to_pos: Optional[Tuple[int, int]] = None,
                  move: Optional[Move] = None) -> bool:
        """
        Moves the tower at `from_pos` on top of the tower at `to_pos` and returns whether this was successful.
        The method does not check whether this move is legal under the current rules.
        It does, however, check whether this move is technically possible, i.e. both positions are distinct and
        contain towers.
        Both positions are 0-indexed and specify the row in the first component and the column in the second.
        If both a move object and explicit positions are given, the positions specified by the move objects are used.
        If a position is not specified in any way, a ValueError is raised.
        Making a skip move will not change the move nor the game field and is considered a successful move.
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :param move: use positions from this move instance instead of from_pos and to_pos
        :return: whether the move was successful
        """
        if move is not None:
            if move.is_skip_move():
                return True

            if move.already_made():
                raise RuntimeError("move has already been made")
            from_pos = move.from_pos
            to_pos = move.to_pos

        if from_pos is None:
            raise ValueError("missing from_pos")

        if to_pos is None:
            raise ValueError("missing to_pos")

        # check whether both positions are different
        if from_pos == to_pos:
            return False

        # check whether there are towers on both positions
        top_tower = self.get_tower_at(from_pos)
        lower_tower = self.get_tower_at(to_pos)

        if top_tower is None or lower_tower is None:
            return False

        # TODO avoid copying by making the move_on_top_of a method of the lower tower
        top_tower_cpy = Tower(structure=top_tower.structure.copy())
        top_tower.move_on_top_of(lower_tower)  # only adds lower_tower to top_tower in the current implementation
        self.set_tower_at(to_pos, top_tower)
        self.set_tower_at(from_pos, None)

        if move is not None:
            move.from_tower = top_tower_cpy

        return True

    def take_back(self, move: Move) -> None:
        """
        Brings the board back to the state before the move. Only works correctly when reverting the most recent move.
        This method will raise all kinds of errors on false inputs:
        - when trying to take back a move that has never been made before
        - if there is a tower at the move's `from_pos` or *no* tower at the move's `to_pos`
        - if the move's `from_tower` is not a the top part of the tower at `move.to_pos`
        Taking back a skip move will not change the move nor the game field.
        :param move: the move to revert
        """
        if move.is_skip_move():
            return

        # check whether the move has been made already
        if not move.already_made():
            raise ValueError("move has not already been made")

        # check whether the game field at from_pos is empty
        # (tower should have been moved by move and no other towers can be moved on empty fields)
        tower_at_from_pos = self.get_tower_at(move.from_pos)
        if not (tower_at_from_pos is None or tower_at_from_pos.height == 0):
            raise RuntimeError(f"tower at {move.from_pos}, which should have been moved earlier by move \"{move}\"")

        # check whether there is a tower at the to_pos that is also high enough
        tower_at_to_pos = self.get_tower_at(move.to_pos)
        if tower_at_to_pos is None or tower_at_to_pos.height < move.from_tower.height:
            raise RuntimeError(
                f"tower at {move.to_pos} missing or too small, can not split to take back move \"{move}\"")

        # check whether the take_back would remove the whole tower at to_pos
        # this would mean that the given move placed a tower on an empty field (which is not permitted)
        # Therefore, an error is raised to find bugs in the algorithm
        if move.from_tower == tower_at_to_pos:
            raise RuntimeError("Can not take back a whole tower")

        tower_at_to_pos.detach(move.from_tower)
        self.set_tower_at(move.from_pos, move.from_tower)

        # mark the move as reversed
        move.from_tower = None

    @staticmethod
    def setup_field(specs: Dict[Tuple[int, int], Tower], min_height: int = 1, min_width: int = 1) -> 'GameField':
        """
        Creates a game field that is filled with empty towers and specified towers at given (by `specs`) positions.
        The returned field is at least height x width tiles in size. The actual size is computed from `specs`.
        Similarly, the player ids are derived from the specified towers. This method currently follows the convention
        that the smaller id corresponds to the first player (possibly causing an error if this is equal to the second
        player's default value).
        :param specs: a dict that specifies which towers to set on the field
        :param min_height: the minimum height of the field
        :param min_width: the minimum width of the field
        :return: a GameField with the specified towers set
        """
        if min_height < 1 or min_width < 1:
            raise ValueError(f"both min_height (given: {min_height}) and min_width ({min_width}) must be at least 1")

        # update min values for field sizes and keep track of tower owners
        players = set()
        for pos in specs.keys():
            min_height = max(min_height, pos[0] + 1)
            min_width = max(min_width, pos[1] + 1)
            players.add(specs[pos].owner)

        # check player constellations
        if len(players) == 0:
            gf = GameField(height=min_height, width=min_width)
        elif len(players) == 1:
            gf = GameField(height=min_height, width=min_width, player1=players.pop())
        elif len(players) == 2:
            players = sorted(list(players))
            gf = GameField(height=min_height, width=min_width, player1=players[0], player2=players[1])
        else:
            raise ValueError("too many tower owners specified")

        # set the field with values
        for x in range(min_height):
            for y in range(min_width):
                pos = (x, y)
                if pos in specs:
                    gf.set_tower_at(pos, specs[pos])
                else:
                    gf.set_tower_at(pos, None)

        return gf

    def __str__(self) -> str:
        """
        Returns a string representation of this game field that is dynamically aligned with the size of the towers.
        :return: a string representation of the game field
        """
        string_repr = ""
        max_tower_height = max(
            map(lambda t: t.height, self.field)) * 3  # x3 because of commas and spaces and +2 because of []
        for x in range(self.height):
            towers_in_that_row = ""
            for y in range(self.width):
                tower_str = self.get_tower_at((x, y)).__str__()
                towers_in_that_row += "{0:>{1}} | ".format(tower_str, max_tower_height)
            string_repr += towers_in_that_row + '\n'
        return string_repr
