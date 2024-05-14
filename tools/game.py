from typing import Union
from tools.hexagons import *
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

#Cell = tuple[int, int]
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
#State = list[tuple[Cell,Player]]
State = dict[Cell, Player]

# -------- Conversion pour adéquation à nos types de données --------

def list_to_dict(state: list[tuple[Cell,Player]]) -> State:
    res: State = {}
    for cell, player in state:
        res[cell] = player
    return res

def dict_to_list(state: State) -> list[tuple[Cell,Player]]:
    res: list[tuple[Cell,Player]] = []
    for cell, player in state.items():
        res.append((cell, player))
    return res

def hex_to_tuple(cell: Cell) -> tuple[int,int]:
    return (cell.q, cell.r)

def tuple_to_hex(cell: tuple[int,int]) -> Cell:
    return Hex(cell[0], cell[1])







# -------- Plateau de jeu --------

class Game:
    def __init__(
        self, game: str, state: State, player: Player, hex_size: int, total_time: Time
    ):
        # add test before creation
        self.game: str = game
        self.state: State = state
        self.player: Player = player
        self.hex_size: int = hex_size
        self.total_time: Time = total_time

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
                color=text_color
            )

        plt.xlim(-2 * self.hex_size, 2 * self.hex_size)
        plt.ylim(-2 * self.hex_size, 2 * self.hex_size)
        plt.show()

Environment = Game







# -------- Initlisation des plateaux de jeu --------

def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    #empty board
    res: State = {}
    n = hex_size
    for r in range(n, -n-1, -1):
        qmin = max(-n, r-n)
        qmax = min(n, r+n)
        for q in range(qmin, qmax+1):
            res[Hex(q, r)] = EMPTY
            if game == "Dodo":
                if -q > r + (hex_size - 3):
                    res[Hex(q, r)] = R
                elif r > -q + (hex_size - 3):
                    res[Hex(q, r)] = B
                else:
                    res[Hex(q, r)] = EMPTY
        if game != "Gopher" and game != "Dodo":
            raise ValueError("game must be 'Dodo' or 'Gopher'")

    return Game(game, res, player, n, total_time)
