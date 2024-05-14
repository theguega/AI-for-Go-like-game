from typing import Union, Callable
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
Evaluation = float
State = dict[Cell, Player]


class Board:
    def __init__(
        self, game: str, state: State, player: Player, hex_size: int, total_time: Time
    ):
        # add test before creation
        self.game: str = game
        self.state: State = state
        self.player: Player = player
        self.hex_size: int = hex_size
        self.total_time: Time = total_time

    def final(self, player: Player) -> bool:
        return len(self.legals(player)) == 0

    def play(self, player: Player, action: Action):
        new_state = self.state.copy()
        new_state[action[0]] = 0
        new_state[action[1]] = player
        return Board(self.game, new_state, 3 - player, self.hex_size, self.total_time)

    def plot(self):
        plt.figure(figsize=(10, 10))
        layout = Layout(layout_ia02, Point(1, -1), Point(0, 0))

        for hexagon, player in self.state.items():
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

        plt.xlim(-2 * self.hex_size, 2 * self.hex_size)
        plt.ylim(-2 * self.hex_size, 2 * self.hex_size)
        plt.show()


Environment = Board


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    res: State = {}
    n = hex_size - 1
    for r in range(n, -n - 1, -1):
        q1 = max(-n, r - n)
        q2 = min(n, r + n)
        if game == "Dodo":
            for q in range(q1, q2 + 1):
                if -q > r + (hex_size - 3):
                    res[Hex(q, r)] = R
                elif r > -q + (hex_size - 3):
                    res[Hex(q, r)] = B
                else:
                    res[Hex(q, r)] = EMPTY
        elif game == "Gopher":
            for q in range(q1, q2 + 1):
                res[Hex(q, r)] = EMPTY
        else:
            raise ValueError("Unknown game")

    return Board(game, res, player, hex_size, total_time)
