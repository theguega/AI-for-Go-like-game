"""Game class and functions"""

from typing import Union
import random
from collections import deque
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
from tools.hexagons import (
    Hex,
    Layout,
    Point,
    layout_ia02,
    polygon_corners,
    hex_to_pixel,
    axial_to_cube,
    DoubledCoord,
)
from client.gndclient import (
    Player,
    Time,
    BLUE,
    RED,
    EMPTY,
    GOPHER_STR,
    DODO_STR,
    Action,
    ActionGopher,
    ActionDodo,
    Score,
)
from tools.mcts import MCTSNode


# --------------------------------------


CellPerso = Hex
StatePerso = dict[CellPerso, Union[Player, int]]
Neighbors = dict[CellPerso, list[CellPerso]]


# --------------------------------------


class Game:
    """Game class"""

    def __init__(
        self,
        game: str,
        state: StatePerso,
        player: Player,
        hex_size: int,
        total_time: Time,
        root: MCTSNode = None,
    ):
        if player not in [RED, BLUE]:
            raise ValueError("player must be 1 or 2")
        if hex_size < 1:
            raise ValueError("hex_size must be >= 1")
        if game not in [GOPHER_STR, DODO_STR]:
            raise ValueError("game must be GOPHER_STR or DODO_STR")
        
        self.cache = {}
        self.game: str = game
        self.state: StatePerso = state
        self.player: Player = player
        self.hex_size: int = hex_size
        self.total_time: Time = total_time
        self.root: MCTSNode = root

    def plot(self):
        """Plot the current state of the game"""
        plt.figure(figsize=(10, 10))
        layout = Layout(layout_ia02, Point(1, -1), Point(0, 0))

        for hexagon, player in self.state.items():
            corners = polygon_corners(layout, hexagon)
            center = hex_to_pixel(layout, hexagon)

            if player == RED:
                color = "red"
                text_color = "white"
            elif player == BLUE:
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
        """Show the current state of the game for 1 second"""
        self.plot()
        plt.pause(1)
        plt.close()

    def final_show(self):
        """Show the final state of the game"""
        self.plot()
        plt.show()

    def final(self) -> bool:
        """Return True if the game is over"""
        return not self.legals()

    def legals(self) -> list[Action]:
        """Return the legal moves for the current player"""
        raise NotImplementedError

    def play(self, action: Action):
        """Play the move"""
        raise NotImplementedError

    def undo(self, action: Action):
        """Undo the move"""
        raise NotImplementedError

    def score(self) -> Score:
        """Return the score of the game"""
        raise NotImplementedError

    def heuristic_evaluation(self, leg) -> Score:
        """Heuristic evaluation based on the number of legals moves"""
        raise NotImplementedError

    def strategy_random(self) -> Action:
        """Random strategy"""
        res: list[Action] = self.legals()
        return random.choice(res)

    def strategy_alpha_beta(self, max_depth=5) -> Action:
        """Alpha beta strategy"""
        return self.alpha_beta(max_depth, -float("inf"), float("inf"))[0]

    def alpha_beta(self, depth: int, alpha: int, beta: int) -> tuple[Action, Score]:
        """Alpha beta algorithm"""
        # recuperation des coups possibles
        leg: list[Action] = self.legals()

        if len(leg) == 0:
            return None, self.score()

        if depth == 0:
            return None, self.heuristic_evaluation(leg)

        if self.player == RED:
            best_score: float = -float("inf")
            best_action: Action = None
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

        best_score: float = float("inf")
        best_action: Action = None
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
    
    def strategy_alpha_beta_cache(self, max_depth=5) -> Action:
        """Alpha beta strategy with cache"""
        return self.alpha_beta_cache(max_depth, -float("inf"), float("inf"))[0]
    
    def alpha_beta_cache(self, depth: int, alpha: int, beta: int) -> tuple[Action, Score]:
        """Alpha beta algorithm with caching of alpha and beta values"""
        state_key = (self.player, frozenset(self.state.items()), depth)  # Create a unique key for the current state with depth

        if state_key in self.cache:
            cached_alpha, cached_beta, cached_result = self.cache[state_key]
            if cached_alpha >= beta:
                return cached_result  # Beta cut-off
            if cached_beta <= alpha:
                return cached_result  # Alpha cut-off
            alpha = max(alpha, cached_alpha)
            beta = min(beta, cached_beta)

        leg: list[Action] = self.legals()

        if len(leg) == 0:
            return None, self.score()

        if depth == 0:
            return None, self.heuristic_evaluation(leg)

        if self.player == RED:
            best_score: float = -float("inf")
            best_action: Action = None
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
            result = (best_action, best_score)
        else:
            best_score: float = float("inf")
            best_action: Action = None
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
            result = (best_action, best_score)

        self.cache[state_key] = (alpha, beta, result)  # Cache the result with alpha and beta values
        return result

    def strategy_mc(self, nb_iter: int) -> Action:
        """Monte Carlo strategy"""
        legals: list[Action] = self.legals()

        if len(legals) == 1:
            return legals[0]

        best_value: int = 0
        best_action: Action = None
        stack: deque = deque()

        for action in legals:
            gain: float = 0
            victoire_rouge: int = 0
            victoire_bleu: int = 0
            stack.append(action)
            self.play(action)

            for _ in range(nb_iter // len(legals) + 1):
                while not self.final():
                    tmp_action: Action = self.strategy_random()
                    stack.append(tmp_action)
                    self.play(tmp_action)
                if self.score() == 100:
                    victoire_rouge += 1
                elif self.score() == -100:
                    victoire_bleu += 1
                while len(stack) > 1:
                    self.undo(stack.pop())

            self.undo(stack.pop())
            if self.player == RED:
                gain = victoire_rouge / nb_iter
            else:
                gain = victoire_bleu / nb_iter
            if gain >= best_value:
                best_value = gain
                best_action = action
        return best_action

    def strategy_mcts(self, time_left: int, root: MCTSNode = None) -> Action:
        """Monte Carlo Tree Search strategy"""
        if not root:
            root: MCTSNode = MCTSNode(self.legals(), self.player)
        root = root.best_action(self, time_left)
        return root.parent_action, root


Environment = Game


class GameGopher(Game):
    """Game Gopher class"""

    def __init__(
        self,
        game: str,
        state: StatePerso,
        player: Player,
        hex_size: int,
        total_time: Time,
        root: MCTSNode = None,
    ):
        # initialisation de la classe mère
        super().__init__(game, state, player, hex_size, total_time,root)

        # initialisation des pions
        self.red_pawns: StatePerso = {}
        self.blue_pawns: StatePerso = {}

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
        """Return the legal moves for the current player"""
        res: list[ActionGopher] = []

        # first move can be anywhere
        if len(self.red_pawns) == 0 and len(self.blue_pawns) == 0:
            # if the board is empty, we place the first pawn in the center
            res.append(axial_to_cube(DoubledCoord(0, self.hex_size - 1)))

        # O(nb_paws) = O(nb_paws)
        for hexagon, _ in (
            self.red_pawns.items() if self.player == BLUE else self.blue_pawns.items()
        ):
            # O(6) = O(1)
            moves: list[CellPerso] = []

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
        """Play the move"""
        # update party state
        self.state[action] = self.player

        # update pawns
        if self.player == RED:
            self.red_pawns[action] = self.player
        else:
            self.blue_pawns[action] = self.player

        self.player = 3 - self.player  # changement de joueur

    def undo(self, action: ActionGopher):
        """ "Undo the move"""
        self.player = 3 - self.player  # repassage au joueur précédent

        # update party state
        self.state[action] = EMPTY

        # update pawns
        if self.player == RED:
            del self.red_pawns[action]
        else:
            del self.blue_pawns[action]

    def score(self) -> Score:
        """Return the score of the game"""
        return -100 if self.player == RED else 100

    def heuristic_evaluation(self, leg) -> Score:
        """Heuristic evaluation based on the number of legals moves"""
        if self.player == RED:
            return len(leg)
        return -len(leg)


class GameDodo(Game):
    """Game Dodo class"""

    def __init__(
        self,
        game: str,
        state: StatePerso,
        player: Player,
        hex_size: int,
        total_time: Time,
        root: MCTSNode = None,
    ):
        # initialisation de la classe mère
        super().__init__(game, state, player, hex_size, total_time,root)

        # initialisation des pions
        self.red_pawns: list[CellPerso] = []
        self.blue_pawns: list[CellPerso] = []
        for hexagon, play in state.items():
            if play == RED:
                self.red_pawns.append(hexagon)
            elif play == BLUE:
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
        """Return the legal moves for the current player"""
        res: list[ActionDodo] = []

        # O(nb_paws*3) = O(nb_paws)
        for hexagon in self.red_pawns if self.player == RED else self.blue_pawns:
            for possible_move in (
                self.red_forward[hexagon]
                if self.player == RED
                else self.blue_forward[hexagon]
            ):
                if self.state[possible_move] == EMPTY:
                    res.append((hexagon, possible_move))

        return res

    def play(self, action: ActionDodo):
        """Play the move"""
        # update party state
        self.state[action[0]] = EMPTY
        self.state[action[1]] = self.player

        # update pawns
        if self.player == RED:
            self.red_pawns.remove(action[0])
            self.red_pawns.append(action[1])
        else:
            self.blue_pawns.remove(action[0])
            self.blue_pawns.append(action[1])

        self.player = 3 - self.player  # changement de joueur

    def undo(self, action: ActionDodo):
        """Undo the move"""
        self.player = 3 - self.player  # repassage au joueur précédent

        # update party state
        self.state[action[0]] = self.player
        self.state[action[1]] = EMPTY

        # update pawns
        if self.player == RED:
            self.red_pawns.remove(action[1])
            self.red_pawns.append(action[0])
        else:
            self.blue_pawns.remove(action[1])
            self.blue_pawns.append(action[0])

    def score(self) -> Score:
        """Return the score of the game"""
        return 100 if self.player == RED else -100

    def heuristic_evaluation(self, leg) -> Score:
        """Heuristic evaluation based on the number of legals moves"""
        # less legals moves is better
        if self.player == RED:
            return -len(leg)
        return len(leg)


# --------------------------------------


def new_dodo(h: int) -> StatePerso:
    """Return a new Dodo grid of size h x h"""
    h = h - 1  # pour avoir un plateau de taille h
    res: StatePerso = {}
    for r in range(h, -h - 1, -1):
        qmin = max(-h, r - h)
        qmax = min(h, r + h)
        for q in range(qmin, qmax + 1):
            res[axial_to_cube(DoubledCoord(q, r))] = EMPTY
            if -q > r + (h - 2):
                res[axial_to_cube(DoubledCoord(q, r))] = RED
            elif r > -q + (h - 2):
                res[axial_to_cube(DoubledCoord(q, r))] = BLUE
    return res


def empty_grid(h: int) -> StatePerso:
    """Return an empty hexagonal grid of size h x h"""
    h = h - 1  # pour avoir un plateau de taille h
    res: StatePerso = {}
    for r in range(h, -h - 1, -1):
        qmin = max(-h, r - h)
        qmax = min(h, r + h)
        for q in range(qmin, qmax + 1):
            res[axial_to_cube(DoubledCoord(q, r))] = EMPTY
    return res
