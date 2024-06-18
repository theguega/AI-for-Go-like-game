"""Monte Carlo Tree Search"""

from collections import defaultdict, deque
import numpy as np
from time import time

from client.gndclient import (
    Action,
    Player,
    BLUE,
)


class MCTSNode:
    """Node of the Monte Carlo Tree Search"""

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

    def q(self) -> int:
        """Return the number of wins of the node"""
        return self._wins - self._loses

    def n(self) -> int:
        """Return the number of visits of the node"""
        return self._number_of_visits

    def expand(self, env):
        """Expand the node with a new child node"""
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
        """Check if the node is a terminal node"""
        return env.final()

    def rollout(self, env) -> int:
        """Simulate a game from the node"""
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
        """Update the node with the result of the simulation"""
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
        """ "Check if the node is fully expanded"""
        return len(self._untried_actions) == 0

    def best_child(self, c_param=np.sqrt(2)):
        """Return the best child of the node"""
        choices_weights = [
            (c.q() / c.n()) + c_param * np.sqrt((np.log(self.n()) / c.n()))
            for c in self.children
        ]
        return self.children[np.argmax(choices_weights)]

    def _tree_policy(self, env):
        """Select the best node to explore"""
        stack: deque[Action] = deque()
        current_node: MCTSNode = self
        while not current_node.is_terminal_node(env):

            if not current_node.is_fully_expanded():
                return current_node.expand(env), stack

            current_node = current_node.best_child()
            stack.append(current_node.parent_action)
            env.play(current_node.parent_action)

        return current_node, stack

    def best_action(self, env, time_left,cut):
        """Return the best action to play"""
        nd: MCTSNode
        stack: deque[Action]
        dep = time()
        while (time() - dep) < time_left/cut:
            nd, stack = self._tree_policy(env)
            reward = nd.rollout(env)
            while len(stack) > 0:
                env.undo(stack.pop())
            nd.backpropagate(reward)

        return self.best_child()
