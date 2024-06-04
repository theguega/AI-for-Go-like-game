from typing import Union
from tools.hexagons import *
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import random
from collections import deque

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
State = dict[Hex, Player]
Neighbors = dict[Hex, list[Hex]]


# -------- Environnement --------


class Game:
    def __init__(
        self,
        game: str,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
    ):
        if player not in [R, B]:
            raise ValueError("player must be 1 or 2")
        if hex_size < 1:
            raise ValueError("hex_size must be >= 1")

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
                color=text_color,
            )
        size = 1.9 * self.hex_size
        plt.xlim(-size, size)
        plt.ylim(-size, size)

    def tmp_show(self):
        self.plot()
        plt.pause(1)
        plt.close()

    def final_show(self):
        self.plot()
        plt.show()

    def final(self) -> bool:
        return not self.legals()

    def strategy_random(self) -> Action:
        res = self.legals()
        return random.choice(res)

    def strategy_alpha_beta(self) -> Action:
        return self.alpha_beta(6, -float("inf"), float("inf"))[0]

    def alpha_beta(self, depth: int, alpha: int, beta: int) -> tuple[Action, Score]:
        # recuperation des coups possibles
        leg = self.legals()

        if len(leg) == 0:
            return None, self.score()

        if depth == 0:
            return None, self.heuristic_evaluation(leg)

        if self.player == R:
            best_score = -float("inf")
            best_action = None
            for action in leg:
                self.play(action)
                _, score = self.alpha_beta(depth - 1, alpha, beta)
                self.undo(action)
                if score > best_score:
                    best_score = score
                    best_action = action
                alpha = max(alpha, best_score)
                if beta <= alpha:
                    break
            return best_action, best_score
        else:
            best_score = float("inf")
            best_action = None
            for action in leg:
                self.play(action)
                _, score = self.alpha_beta(depth - 1, alpha, beta)
                self.undo(action)
                if score < best_score:
                    best_score = score
                    best_action = action
                beta = min(beta, best_score)
                if beta <= alpha:
                    break
            return best_action, best_score

    def monte_carlo(self,nb_iter:int) -> Action:
        legals = self.legals()
        max:int = 0
        best_action : Action = None
        tmp_env = None
        stack:deque = deque()
        for action in legals:
            gain:int = 0
            victoire_rouge : int = 0
            victoire_bleu: int = 0
            stack.append(action)
            self.play(action)
            for i in range(nb_iter//len(legals)):
                while not self.final():
                    tmp_action = self.strategy_random()
                    stack.append(tmp_action)
                    self.play(tmp_action)
                if self.score() == 100:
                    victoire_rouge += 1
                elif self.score() == -100:
                    victoire_bleu += 1
                while len(stack)>1:
                    self.undo(stack.pop())
            self.undo(stack.pop())
            if self.player == R:
                gain = victoire_rouge / nb_iter
            else:
                gain = victoire_bleu / nb_iter

            if gain > max:
                max = gain
                best_action = action
        if best_action is None:
            print("mizeuhfpaizyeaezpiyfbzepiucbvaezucbzerurcvbezrcouv\n\n\n")
            env.show()
        return best_action


Environment = Game


class GameGopher(Game):
    def __init__(
        self,
        game: str,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
    ):
        # initialisation de la classe mère
        super().__init__(game, state, player, hex_size, total_time)

        # initialisation des pions
        self.red_pawns: State = {}
        self.blue_pawns: State = {}

        # initilisations de tous les voisins
        neighbor_gopher = [
            axial_to_cube(DoubledCoord(-1, 0)),
            axial_to_cube(DoubledCoord(-1, -1)),
            axial_to_cube(DoubledCoord(0, -1)),
            axial_to_cube(DoubledCoord(0, 1)),
            axial_to_cube(DoubledCoord(1, 1)),
            axial_to_cube(DoubledCoord(1, 0)),
        ]

        self.neighbors: Neighbors = {}

        for hexagon, _ in state.items():
            self.neighbors[hexagon] = []

            for n in neighbor_gopher:
                neighbor = Hex(hexagon.q + n.q, hexagon.r + n.r, hexagon.s + n.s)
                if neighbor in state:
                    self.neighbors[hexagon].append(neighbor)

    def legals(self) -> list[ActionGopher]:
        """
        Red begins the game by placing a stone anywhere on the board. Then, starting with Blue, players take turns placing a stone which forms exactly one enemy connection and no friendly connections
        """
        res: list[ActionGopher] = []

        # first move can be anywhere
        if len(self.red_pawns) == 0 and len(self.blue_pawns) == 0:
            for hexagon, _ in self.state.items():
                res.append(hexagon)
            return res

        # else, we we can place a pawn on a cell that has exactly one enemy connection and no friendly connections
        # O(nb_paws) = O(nb_paws)
        for hexagon, _ in (
            self.red_pawns.items() if self.player == B else self.blue_pawns.items()
        ):
            # O(6) = O(1)
            moves: list[Cell] = []

            for neighbor in self.neighbors[hexagon]:
                if self.state[neighbor] == EMPTY:
                    moves.append(neighbor)
            # O(6*6) = O(1)
            for move in moves:
                enemy: int = 0
                friendly: int = 0
                for n in self.neighbors[move]:
                    if self.state[n] == self.player:
                        friendly += 1
                    elif self.state[n] == 3 - self.player:
                        enemy += 1
                if enemy == 1 and friendly == 0:
                    res.append(move)

        return res

    def play(self, action: ActionGopher):
        # update party state
        self.state[action] = self.player

        # update pawns
        if self.player == R:
            self.red_pawns[action] = self.player
        else:
            self.blue_pawns[action] = self.player

        self.player = 3 - self.player  # changement de joueur

    def undo(self, action: ActionGopher):
        self.player = 3 - self.player  # repassage au joueur précédent

        # update party state
        self.state[action] = EMPTY

        # update pawns
        if self.player == R:
            del self.red_pawns[action]
        else:
            del self.blue_pawns[action]

    def score(self) -> Score:
        return -100 if self.player == R else 100

    def heuristic_evaluation(self, leg) -> Score:
        if self.player == R:
            return len(self.red_pawns) / len(leg)
        else:
            return -len(self.blue_pawns) / len(leg)


class GameDodo(Game):
    def __init__(
        self,
        game: str,
        state: State,
        player: Player,
        hex_size: int,
        total_time: Time,
    ):
        # initialisation de la classe mère
        super().__init__(game, state, player, hex_size, total_time)

        # initialisation des pions
        self.red_pawns: list[Cell] = []
        self.blue_pawns: list[Cell] = []
        for hexagon, play in state.items():
            if play == R:
                self.red_pawns.append(hexagon)
            elif play == B:
                self.blue_pawns.append(hexagon)

        # initilisations de tous les voisins
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

        self.red_forward: Neighbors = {}
        self.blue_forward: Neighbors = {}

        for hexagon, _ in state.items():
            self.red_forward[hexagon] = []
            self.blue_forward[hexagon] = []

            for n_red in forward_red:
                neighbor_red = Hex(
                    hexagon.q + n_red.q, hexagon.r + n_red.r, hexagon.s + n_red.s
                )
                if neighbor_red in state:
                    self.red_forward[hexagon].append(neighbor_red)
            for n_blue in forward_blue:
                neighbor_blue = Hex(
                    hexagon.q + n_blue.q, hexagon.r + n_blue.r, hexagon.s + n_blue.s
                )
                if neighbor_blue in state:
                    self.blue_forward[hexagon].append(neighbor_blue)

    def legals(self) -> list[ActionDodo]:
        """
        All moves are to unoccupied cells. Players can move their checkers one cell directly forward or diagonally forward.
        """
        res: list[ActionDodo] = []

        # O(nb_paws*3) = O(nb_paws)
        for hexagon in self.red_pawns if self.player == R else self.blue_pawns:
            for possible_move in (
                self.red_forward[hexagon]
                if self.player == R
                else self.blue_forward[hexagon]
            ):
                if self.state[possible_move] == EMPTY:
                    res.append((hexagon, possible_move))

        return res

    def play(self, action: ActionDodo):
        # update party state
        self.state[action[0]] = EMPTY
        self.state[action[1]] = self.player

        # update pawns
        if self.player == R:
            self.red_pawns.remove(action[0])
            self.red_pawns.append(action[1])
        else:
            self.blue_pawns.remove(action[0])
            self.blue_pawns.append(action[1])

        self.player = 3 - self.player  # changement de joueur

    def undo(self, action: ActionDodo):
        self.player = 3 - self.player  # repassage au joueur précédent

        # update party state
        self.state[action[0]] = self.player
        self.state[action[1]] = EMPTY

        # update pawns
        if self.player == R:
            self.red_pawns.remove(action[1])
            self.red_pawns.append(action[0])
        else:
            self.blue_pawns.remove(action[1])
            self.blue_pawns.append(action[0])

    def score(self) -> Score:
        return 100 if self.player == R else -100

    def heuristic_evaluation(self, legals) -> Score:
        # less legals moves is better
        if self.player == R:
            score1 = (len(self.red_pawns) * 3) / len(legals)
        else:
            score1 = -(len(self.blue_pawns) * 3) / len(legals)

        # mean of the height of the pawns
        if self.player == R:
            score2 = sum([pawn.r for pawn in self.red_pawns]) / len(self.red_pawns)
        else:
            score2 = sum([pawn.r for pawn in self.blue_pawns]) / len(self.blue_pawns)
        return score1 + score2




# -------- Initlisation des plateaux de jeu --------


def new_dodo(h: int) -> State:
    h = h - 1  # pour avoir un plateau de taille h
    res: State = {}
    for r in range(h, -h - 1, -1):
        qmin = max(-h, r - h)
        qmax = min(h, r + h)
        for q in range(qmin, qmax + 1):
            res[axial_to_cube(DoubledCoord(q, r))] = EMPTY
            if -q > r + (h - 2):
                res[axial_to_cube(DoubledCoord(q, r))] = R
            elif r > -q + (h - 2):
                res[axial_to_cube(DoubledCoord(q, r))] = B
    return res


def new_gopher(h: int) -> State:
    h = h - 1  # pour avoir un plateau de taille h
    res: State = {}
    for r in range(h, -h - 1, -1):
        qmin = max(-h, r - h)
        qmax = min(h, r + h)
        for q in range(qmin, qmax + 1):
            res[axial_to_cube(DoubledCoord(q, r))] = EMPTY
    return res


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """
    Initialize the environment with the game, the state, the player, the hex_size and the total_time
    """
    if game == "Gopher":
        env = GameGopher(game, state, player, hex_size, total_time)
    elif game == "Dodo":
        env = GameDodo(game, state, player, hex_size, total_time)
    else:
        raise ValueError("game must be 'Gopher' or 'Dodo'")
    return env
