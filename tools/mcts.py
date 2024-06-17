import numpy as np
from collections import defaultdict, deque
from typing import *

from tools.game import *
from client.gndclient import *


class MCTSNode:
    def __init__(
        self, leg: list[Action], player: Player, parent=None, parent_action=None
    ):
        self.parent: MCTSNode = parent
        self.associated_player: Player = player
        self.parent_action: Action = parent_action
        self.children: list[MCTSNode] = []
        self._number_of_visits: int = 0
        self._results: defaultdict[int] = defaultdict(int)
        self._wins: int = 0
        self._loses: int = 0
        self._untried_actions: list[Action] = None
        self._untried_actions = leg
        return

    def q(self) -> int:
        return self._wins - self._loses

    def n(self) -> int:
        return self._number_of_visits

    def expand(self, env):
        action: Action = self._untried_actions.pop()
        env.play(action)
        leg: list[Action] = env.legals()
        child_node = MCTSNode(
            leg, self.associated_player, parent=self, parent_action=action
        )
        env.undo(action)
        self.children.append(child_node)
        return child_node

    def is_terminal_node(self, env) -> bool:
        return env.final()

    def rollout(self, env) -> int:
        stack: deque = deque()
        while not env.final():
            action: Action = env.strategy_random()
            stack.append(action)
            env.play(action)

        score: int = env.score()
        while len(stack) > 0:
            env.undo(stack.pop())
        return score

    def backpropagate(self, result: int):
        self._number_of_visits += 1.0
        if self.associated_player == BLUE:
            if result == -100:
                self._wins += 1
            else:
                self._loses += 1
        else:
            if result == 100:
                self._wins += 1
            else:
                self._loses += 1
        if self.parent:
            self.parent.backpropagate(result)

    def is_fully_expanded(self) -> bool:
        return len(self._untried_actions) == 0

    def best_child(self, c_param=np.sqrt(2)):

        choices_weights = [
            (c.q() / c.n()) + c_param * np.sqrt((np.log(self.n()) / c.n()))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def _tree_policy(self, env):

        stack: deque[Action] = deque()
        current_node: MCTSNode = self
        while not current_node.is_terminal_node(env):

            if not current_node.is_fully_expanded():
                return current_node.expand(env), stack
            else:
                current_node = current_node.best_child()
                stack.append(current_node.parent_action)
                env.play(current_node.parent_action)

        return current_node, stack

    def best_action(self, env, nb_simu=1000):
        nd: MCTSNode
        stack: deque[Action]
        for i in range(nb_simu):
            nd, stack = self._tree_policy(env)
            reward = nd.rollout(env)
            while len(stack) > 0:
                env.undo(stack.pop())
            nd.backpropagate(reward)

        return self.best_child()
