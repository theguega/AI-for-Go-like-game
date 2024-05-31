from tools.game import *
import numpy as np
from collections import defaultdict,deque
from typing import *
from copy import deepcopy

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


class MCTSNode:
    def __init__(self, env, parent=None, parent_action=None):
        self.env: Game = env
        self.parent: MCTSNode = parent
        self.parent_action = parent_action
        self.children : list[MCTSNode] = []
        self._number_of_visits: int = 0
        self._results: defaultdict[int] = defaultdict(int)
        self._results[1]: int = 0
        self._results[-1]: int  = 0
        self._untried_actions = None
        self._untried_actions = self.env.legals()
        return

    def q(self) -> int:
        wins: int = self._results[1]
        loses: int = self._results[-1]
        return wins - loses

    def n(self) -> int:
        return self._number_of_visits

    def expand(self):
        action = self._untried_actions.pop()
        self.env.play(action)
        child_node = MCTSNode(deepcopy(self.env), parent=self, parent_action=action)
        self.env.undo(action)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self) -> bool:
        return self.env.final()

    def rollout(self) -> int :
        stack : deque = deque()

        while not self.env.final():
            action = self.env.strategy_random()
            stack.append(action)
            self.env.play(action)

        #self.env.tmp_show()
        score : int = self.env.score()

        while len(stack)>0:
            self.env.undo(stack.pop())
        if self.env.player == B:
            score = -score
        return score//100

    def backpropagate(self, result):
        self._number_of_visits += 1.
        self._results[result] += 1.
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self) -> bool:
        return len(self._untried_actions) == 0

    def best_child(self, c_param=0.1):
        if len(self.children)==0:
            print("Avant erreur:")
            #self.env.tmp_show()
            print(self.env.legals())

        choices_weights = [(c.q() / c.n()) + c_param * np.sqrt((2 * np.log(self.n()) / c.n())) for c in self.children]

        return self.children[np.argmax(choices_weights)]

    def _tree_policy(self):

        current_node = self
        while not current_node.is_terminal_node():

            if not current_node.is_fully_expanded():
                return current_node.expand()
            else:
                current_node = current_node.best_child()
        return current_node


    def best_action(self,nb_simu=1000) :
        v = None
        for i in range(nb_simu):
            v = self._tree_policy()
            reward = v.rollout()
            v.backpropagate(reward)

        return self.best_child(c_param=0.1)

