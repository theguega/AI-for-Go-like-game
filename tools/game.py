from typing import Union
from tools.hexagons import *
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import random

Cell = Hex
ActionGopher = Cell
ActionDodo = tuple[Cell, Cell]  # case de départ -> case d'arrivée
Action = Union[ActionGopher, ActionDodo]
Player = int  # 1 ou 2
R = 1
B = 2
EMPTY = 0
Score = int
Time = int
Case = collections.namedtuple("Case", ["Hex", "Player"])
State = tuple[Case, ...]


# -------- Coversion pour passage mutable - non-mutable --------
def state_to_dict(state: State) -> dict[Hex, Player]:
    res = {}
    for case in state:
        res[case.Hex] = case.Player
    return res


def dict_to_state(d: dict[Hex, Player]) -> State:
    res = []
    for hex, player in d.items():
        res += (Case(hex, player),)
    return tuple(res)


# -------- Environnement --------


class Game:
    def __init__(
        self,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        red_pawns: State = (),
        blue_pawns: State = (),
    ):
        if player not in [R, B]:
            raise ValueError("player must be 1 or 2")
        if hex_size < 1:
            raise ValueError("hex_size must be >= 1")
        # if not valid(state) : error

        self.state: State = state
        self.player: Player = player
        self.hex_size: int = hex_size
        self.total_time: Time = total_time
        self.red_pawns: State = red_pawns
        self.blue_pawns: State = blue_pawns

    def plot(self):
        plt.figure(figsize=(10, 10))
        layout = Layout(layout_ia02, Point(1, -1), Point(0, 0))

        for hexagon, player in self.state:
            corners = polygon_corners(layout, hexagon)
            center = hex_to_pixel(layout, hexagon)

            if player == R:
                color = "red"
                text_color = "white"
            elif player == B:
                color = "blue"
                text_color = "white"
            else:
                color = "white"
                text_color = "black"

            polygon = Polygon(corners, edgecolor="black", facecolor=color, linewidth=2)

            plt.gca().add_patch(polygon)
            plt.text(
                center.x,
                center.y,
                f"{hexagon.q}, {hexagon.r}",
                ha="center",
                va="center",
                color=text_color,
            )
        size = 1.9 * self.hex_size
        plt.xlim(-size, size)
        plt.ylim(-size, size)
        plt.show()

    def final(self) -> bool:
        return not self.legals()

    def score(self) -> Score:
        return 1 if self.player == R else -1

    def strategy_random(self) -> ActionDodo:
        return random.choice(self.legals())


Environment = Game


class GameGopher(Game):
    def __init__(
        self,
        game: str,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        red_pawns: State = (),
        blue_pawns: State = (),
    ):
        super().__init__(state, player, hex_size, total_time, red_pawns, blue_pawns)
        self.game = game
        self.initial_state: bool = False

    def empty(self) -> bool:
        bool = True
        for _, player in self.state:
            if player != EMPTY:
                bool = False
        return bool

    def legals(self) -> list[ActionGopher]:
        """
        Red begins the game by placing a stone anywhere on the board. Then, starting with Blue, players take turns placing a stone which forms exactly one enemy connection and no friendly connections
        """
        res: set[ActionGopher] = set()

        # first move can be anywhere
        if self.initial_state:
            for hexagon, _ in self.state:
                res.add(hexagon)
            res = list(res)
            debug(res)
            return res

        neighbor = [
            axial_to_cube(DoubledCoord(-1, 0)),
            axial_to_cube(DoubledCoord(-1, -1)),
            axial_to_cube(DoubledCoord(0, -1)),
            axial_to_cube(DoubledCoord(0, 1)),
            axial_to_cube(DoubledCoord(1, 1)),
            axial_to_cube(DoubledCoord(1, 0)),
        ]

        dict = state_to_dict(self.state)

        # for every enemy paws, check all neighbors and for every neighbor, count number of friendly and enemy paws
        # O(nb_paws_enemy*6) = O(nb_paws_enemy)
        for hexagon, _ in self.red_pawns if self.player == B else self.blue_pawns:
            moves: State = ()
            # O(6) = O(1)
            for n in neighbor:
                move = hex_add(hexagon, n)
                if move in dict:
                    moves += (Case(move, dict[move]),)

            # O(6*6) = O(1)
            for move, play in moves:
                if play == EMPTY:
                    enemy: int = 0
                    friendly: int = 0
                    # O(6) = O(1)
                    for n in neighbor:
                        nei = hex_add(move, n)
                        if nei in dict and dict[nei] == self.player:
                            friendly += 1
                        elif nei in dict and dict[nei] == 3 - self.player:
                            enemy += 1
                    if enemy == 1 and friendly == 0:
                        res.add(move)
        
        res = list(res)
        debug(res)
        return res

    def play(self, action: ActionGopher) -> Environment:
        # update party state
        state = state_to_dict(self.state)
        state[action] = self.player

        # update pawns
        if self.player == R:
            red_pawns = state_to_dict(self.red_pawns)
            red_pawns[action] = self.player
            self.red_pawns = dict_to_state(red_pawns)
        else:
            blue_pawns = state_to_dict(self.blue_pawns)
            blue_pawns[action] = self.player
            self.blue_pawns = dict_to_state(blue_pawns)

        return GameGopher(
            "Gopher",
            dict_to_state(state),
            3 - self.player,
            self.hex_size,
            self.total_time,
            red_pawns=self.red_pawns,
            blue_pawns=self.blue_pawns,
        )


class GameDodo(Game):
    def __init__(
        self,
        game: str,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
        red_pawns: State = (),
        blue_pawns: State = (),
    ):
        super().__init__(state, player, hex_size, total_time, red_pawns, blue_pawns)
        self.game = game
        self.initial_state: bool = False

    def legals(self) -> list[ActionDodo]:
        """
        All moves are to unoccupied cells. Players can move their checkers one cell directly forward or diagonally forward.
        """
        res: set[ActionDodo] = set()

        forward_blue = [
            axial_to_cube(DoubledCoord(-1, 0)),
            axial_to_cube(DoubledCoord(-1, -1)),
            axial_to_cube(DoubledCoord(0, -1)),
        ]
        forward_red = [
            axial_to_cube(DoubledCoord(0, 1)),
            axial_to_cube(DoubledCoord(1, 1)),
            axial_to_cube(DoubledCoord(1, 0)),
        ]

        dict = state_to_dict(self.state)

        # O(nb_paws*6) = O(nb_paws)
        for hexagon, player in self.red_pawns if self.player == R else self.blue_pawns:
            if player == self.player:
                #O(6) = O(1)
                for possible_move in forward_blue if player == B else forward_red:
                    move = hex_add(hexagon, possible_move)
                    if move in dict and dict[move] == EMPTY:
                        res.add((hexagon, move))

        debug(res)
        return list(res)

    def play(self, action: ActionDodo) -> Environment:
        # update party state
        state = state_to_dict(self.state)
        state[action[0]] = EMPTY
        state[action[1]] = self.player
        self.state = dict_to_state(state)

        # update pawns
        if self.player == R:
            red_pawns = state_to_dict(self.red_pawns)
            red_pawns[action[0]] = EMPTY
            red_pawns[action[1]] = self.player
            self.red_pawns = dict_to_state(red_pawns)
        else:
            blue_pawns = state_to_dict(self.blue_pawns)
            blue_pawns[action[0]] = EMPTY
            blue_pawns[action[1]] = self.player
            self.blue_pawns = dict_to_state(blue_pawns)

        return GameDodo(
            "Dodo",
            self.state,
            3 - self.player,
            self.hex_size,
            self.total_time,
            red_pawns=self.red_pawns,
            blue_pawns=self.blue_pawns,
        )


# -------- Initlisation des plateaux de jeu --------


def new_dodo(h: int) -> State:
    res: State = ()
    for r in range(h, -h - 1, -1):
        qmin = max(-h, r - h)
        qmax = min(h, r + h)
        for q in range(qmin, qmax + 1):
            res += (Case(axial_to_cube(DoubledCoord(q, r)), EMPTY),)
            if -q > r + (h - 2):
                res += (Case(axial_to_cube(DoubledCoord(q, r)), R),)
            elif r > -q + (h - 2):
                res += (Case(axial_to_cube(DoubledCoord(q, r)), B),)
    return res


def new_gopher(h: int) -> State:
    res: State = ()
    for r in range(h, -h - 1, -1):
        qmin = max(-h, r - h)
        qmax = min(h, r + h)
        for q in range(qmin, qmax + 1):
            res += (Case(axial_to_cube(DoubledCoord(q, r)), EMPTY),)
    return res


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """
    Initialize the environment with the game, the state, the player, the hex_size and the total_time
    """
    if game == "Gopher":
        env = GameGopher(game, state, player, hex_size, total_time)
        if env.empty():
            env.initial_state = True
    elif game == "Dodo":
        # init pawns of each player
        red_pawns: State = ()
        blue_pawns: State = ()
        for hexagon, player in state:
            if player == R:
                red_pawns += (Case(hexagon, player),)
            elif player == B:
                blue_pawns += (Case(hexagon, player),)
        # create environment
        env = GameDodo(game, state, player, hex_size, total_time, red_pawns, blue_pawns)
    else:
        raise ValueError("game must be 'Gopher' or 'Dodo'")
    return env


def debug(res: list[Action]):
    pass
    # print("--------------------")
    # for actions in res:
    #    print(actions)
