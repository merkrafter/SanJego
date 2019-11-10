import copy
from typing import Optional, Iterator, Sequence, Dict, Tuple

from src import Searching


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
        # TODO make this a method of the lower tower and change the GameField method accordingly
        if tower is None:
            raise ValueError("can not move this tower on top of None")
        if self.structure is None or tower.structure is None:
            raise ValueError("can not move empty towers on top of each other")
        self.structure += tower.structure

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

    def make_move(self, from_pos: (int, int), to_pos: (int, int)) -> bool:
        """
        Moves the tower at `from_pos` on top of the tower at `to_pos` and returns whether this was successful.
        The method does not check whether this move is legal under the current rules.
        It does, however, check whether this move is technically possible, i.e. both positions are distinct and
        contain towers.
        Both positions are 0-indexed and specify the row in the first component and the column in the second.
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :return: whether the move was successful
        """
        # check whether both positions are different
        if from_pos == to_pos:
            return False

        # check whether there are towers on both positions
        top_tower = self.get_tower_at(from_pos)
        lower_tower = self.get_tower_at(to_pos)

        if top_tower is None or lower_tower is None:
            return False

        top_tower.move_on_top_of(lower_tower)  # only adds lower_tower to top_tower in the current implementation
        self.set_tower_at(to_pos, top_tower)
        self.set_tower_at(from_pos, None)
        return True

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


class RuleSet(object):
    """
    This class provides methods that define the rules of the game and its win conditions.
    All methods are read-only with respect to the GameField.
    """

    def __init__(self, game_field: GameField) -> None:
        """
        Creates a new RuleSet based on the given game field. The game field is never changed by a `RuleSet`.
        :param game_field:
        """
        self.game_field = game_field

    def player_may_move_tower(self, player: int, tower: Tower) -> bool:
        """
        Decides whether the given player is allowed to move `tower`.
        Using this rule set, a player is allowed to move a tower if at least half of the bricks of that tower belong to
        the player. Owning the tower is **not** a requirement.
        This method does not check whether `tower` is actually on the game field.
        :param player: ID of a player that is registered in the `GameField` instance of this `RuleSet`
        :param tower: a tower instance that the players wants to move
        :return: whether the player is allowed to move the tower given this rule set
        """
        player1: int = self.game_field.player1
        player2: int = self.game_field.player2

        share_player1: int = sum(map(lambda brick: brick == player1, tower.structure))
        share_player2: int = sum(map(lambda brick: brick == player2, tower.structure))

        return player == player1 and share_player1 >= share_player2 or \
               player == player2 and share_player2 >= share_player1

    def allows_move(self, from_pos: (int, int), to_pos: (int, int), player: int) -> bool:
        """
        Decides whether the given player is allowed to make the move given by the two positions on the board.
        Using this rule set, a player is allowed to make that move if
        - he may move the tower at `from_pos` at all
        - `to_pos` is in the king's/8's neighbourhood of `from_pos` **and**
        - there are towers at both positions that have different owners.
        :param from_pos: specifies the tower to move
        :param to_pos: specifies the tower to move on top of
        :param player: ID of a player that is registered in the `GameField` instance of this `RuleSet`
        :return: whether the player is allowed to make this move given this rule set
        """
        # check whether both positions are neighbours (king's neighbourhood)
        if not (-1 <= (from_pos[0] - to_pos[0]) <= 1 and -1 <= (from_pos[1] - to_pos[1]) <= 1):
            return False

        # check whether both positions are on the board and
        # check whether there are towers on both positions
        top_tower = self.game_field.get_tower_at(from_pos)
        lower_tower = self.game_field.get_tower_at(to_pos)
        if top_tower is None or lower_tower is None or top_tower.height == 0 or lower_tower.height == 0:
            return False

        # check whether both towers are not identical and
        # check whether both towers have different owners (note that the latter prevents the former in this rule set)
        if top_tower.owner == lower_tower.owner:
            return False

        # check whether the player is allowed to move the tower at from_pos at all
        return self.player_may_move_tower(player, top_tower)


class GameNode(Searching.Node):
    """
    Represents a state of San Jego. It provides methods to iterate over all descending game states, and receive the
    value of this game state.
    """

    def __init__(self, game_field: GameField, rule_set: RuleSet, max_player: bool = True) -> None:
        """
        Creates a new `GameNode` by setting the game field, rule set and player given as arguments.
        If `player` is omitted, it is set to `game_field`'s `player1` attribute.
        :param game_field:
        :param rule_set:
        :param max_player: whether the maximising player moves next
        """
        # both parameters can not be None, because it is not clear what RuleSet to use in that case
        self.game_field = game_field
        self.rule_set = rule_set
        self.max_player = max_player
        if self.max_player:
            self.player = self.game_field.player1
        else:
            self.player = self.game_field.player2

    def children(self) -> Iterator['GameNode']:
        """
        Iterates over all possible/allowed following game states.
        :return: iterator over all following game states
        """
        # iterate over any position on the field
        for from_pos in [(x, y) for x in range(self.game_field.height) for y in range(self.game_field.width)]:

            # iterate over the king's neighbourhood of from_pos...
            for to_pos in [(x, y) for x in [from_pos[0] - 1, from_pos[0], from_pos[0] + 1]
                           for y in [from_pos[1] - 1, from_pos[1], from_pos[1] + 1]]:

                # ... and yield any allowed moves
                if self.rule_set.allows_move(from_pos, to_pos, self.player):
                    gf = copy.deepcopy(self.game_field)
                    gf.make_move(from_pos, to_pos)
                    yield GameNode(gf, RuleSet(gf), not self.max_player)

    def value(self) -> int:
        """
        Computes the value of this `GameNode`, defined as the value of its `game_field`.
        :return: value of this node's `game_field`
        """
        return self.game_field.value

    def __str__(self) -> str:
        """
        Returns a string representation of this game node that contains the player to move and the game field string.
        :return: a string representation of this game node
        """
        return f"turn of player {self.player}\n" + self.game_field.__str__()


if __name__ == "__main__":
    gf = GameField(5, 4)
    print(f"game value after initialization: {gf.value} (should be 0)")

    rs = RuleSet(gf)
    if rs.allows_move((0, 0), (0, 1), gf.player1):
        gf.make_move((0, 0), (0, 1))
        print(f"game value after move (0,0) -> (0,1): {gf.value} (should be 1)")
    else:
        import sys

        print(f"Could not make legal move (0,0) -> (0,1)", file=sys.stderr)

    gn = GameNode(gf, rs)
    value = Searching.alpha_beta_search(gn, 2, maximising_player=False)
    print(f"value of this game from here: {value}")
