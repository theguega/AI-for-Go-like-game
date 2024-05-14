from typing import Union
from tools.hexagons import *
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon

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
State = dict[Cell, Player]

# -------- Conversion pour adéquation à nos types de données --------
def list_to_dict(state: list[tuple[Cell, Player]]) -> State:
    """
    Convertit une liste de tuples en dictionnaire
    """
    return {cell: player for cell, player in state}

def dict_to_list(state: State) -> list[tuple[Cell, Player]]:
    """
    Convertit un dictionnaire en liste de tuples
    """
    return [(cell, player) for cell, player in state.items()]

def tuple_to_hex(t: tuple[int, int]) -> Cell:
    """
    Convertit un tuple en Hex
    """
    return axial_to_cube(DoubledCoord(t[0], t[1]))

def hex_to_tuple(h: Cell) -> tuple[int, int]:
    """
    Convertit un Hex en tuple
    """
    return (h.q, h.r)






# -------- Plateau de jeu --------

class Game:
    def __init__(
        self, game: str, state: State, player: Player, hex_size: int, total_time: Time
    ):
        """
        Constructeur de la classe Game
        """
        # add test before creation
        if game not in ["Gopher", "Dodo"]:
            raise ValueError("game must be 'Gopher' or 'Dodo'")
        if player not in [R, B]:
            raise ValueError("player must be 1 or 2")
        if hex_size < 1:
            raise ValueError("hex_size must be >= 1")
        #if not valid(state) : error
        
        self.game: str = game
        self.state: State = state
        self.player: Player = player
        self.hex_size: int = hex_size
        self.total_time: Time = total_time

    def plot(self):
        """
        Affiche le plateau de jeu actuel
        """
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

        plt.xlim(-3 * self.hex_size, 3 * self.hex_size)
        plt.ylim(-3 * self.hex_size, 3 * self.hex_size)
        plt.show()

Environment = Game 







# -------- Initlisation des plateaux de jeu --------

def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """
    Initialise un plateau de jeu à l'état initial en fonction du type de jeu
    """
    res: State = {}
    h = hex_size
    for r in range(h, -h-1, -1):
        qmin = max(-h, r-h)
        qmax = min(h, r+h)
        for q in range(qmin, qmax+1):
            res[axial_to_cube(DoubledCoord(q, r))] = EMPTY
            if game == "Dodo":
                if -q > r + (hex_size - 3):
                    res[axial_to_cube(DoubledCoord(q, r))] = R
                elif r > -q + (hex_size - 3):
                    res[axial_to_cube(DoubledCoord(q, r))] = B

    return Game(game, res, player, h, total_time)
