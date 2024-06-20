"""Main file to run the client on the server"""

import argparse
from client.gndclient import (
    start,
    Cell,
    Action,
    Score,
    Player,
    State,
    Time,
    RED,
    BLUE,
    EMPTY,
    DODO_STR,
    GOPHER_STR,
)
from tools.game import (
    CellPerso,
    StatePerso,
    Environment,
    axial_to_cube,
    DoubledCoord,
    empty_grid,
    GameDodo,
    GameGopher,
)

# game settings
DODO_DEPTH = 6
DODO_NB_SIMU = 5000

GOPHER_DEPTH = 8
GOPHER_NB_SIMU = 2500


# --------------------------------------


def cell_to_cellperso(cell: Cell) -> CellPerso:
    """Convert a tuple[int, int] to a Hex for use in the API"""
    return axial_to_cube(DoubledCoord(cell[0], cell[1]))


def cellperso_to_cell(cell: CellPerso) -> Cell:
    """Convert a Hex to a tuple[int, int] for use in the API"""
    return (cell.q, cell.r)


def get_action(env: Environment, new_state: State) -> Action:
    """Get the action of the opponent from the new state of the game"""
    # Gopher
    if env.game == GOPHER_STR:
        # Find the cell that appeared in the new state (destination)
        for pos, player in new_state:
            if player != EMPTY:
                hexa = cell_to_cellperso(pos)
                if env.state[hexa] == EMPTY:
                    return hexa
        return None

    # Dodo
    # Find the cell that disappeared in the old state (source)
    source: CellPerso = None
    for hexa, player in env.state.items():
        if player != EMPTY:
            pos: Cell = cellperso_to_cell(hexa)
            for cell2, player2 in new_state:
                if player2 == EMPTY and pos == cell2:
                    source = hexa
                    break

    # Find the cell that appeared in the new state (destination)
    destination: CellPerso = None
    for pos, player in new_state:
        if player != EMPTY:
            hexa = cell_to_cellperso(pos)
            if env.state[hexa] == EMPTY:
                destination = hexa
                break

    if source is None or destination is None:
        return None

    return (source, destination)


# --------------------------------------


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """Initialize the environment"""

    initial_state: StatePerso = empty_grid(hex_size)

    if game == GOPHER_STR:
        env = GameGopher(game, initial_state, player, hex_size, total_time)
        # synchronize the state of the game with the state given by the server
        for pos, play in state:
            hexa = cell_to_cellperso(pos)
            env.state[hexa] = play
            if play == RED:
                env.red_pawns[hexa] = RED
            elif play == BLUE:
                env.blue_pawns[hexa] = BLUE

    else:
        env = GameDodo(game, initial_state, player, hex_size, total_time)
        # synchronize the state of the game with the state given by the server
        for pos, play in state:
            hexa = cell_to_cellperso(pos)
            env.state[hexa] = play
            if play == RED:
                env.red_pawns.append(hexa)
            elif play == BLUE:
                env.blue_pawns.append(hexa)
    return env


# --------------------------------------


def final_result(state: State, score: Score, player: Player):
    """Print the final result of the game"""
    print(f"Ending: {player} wins with a score of {score}")


# --------------------------------------


def strategy(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    """Strategy of depend on game"""
    # update the env with the action of the opponent
    opponent_action: Action = get_action(env, state)
    # if using MCTS, update of the root
    if env.root:
        for child in env.root.children:
            if child.parent_action == opponent_action:
                env.root = child

    if opponent_action is not None:
        env.play(opponent_action)

    # print the time remaining for the player
    print(f"Time remaining for player {player} : {time_left}")

    # playing the best action
    if env.game == DODO_STR:
        best_action, env.root = env.strategy_mcts(DODO_NB_SIMU,env.root)
    else:
        best_action = env.strategy_alpha_beta_cache(GOPHER_DEPTH)
    env.play(best_action)

    # convert the action for the api
    if env.game == GOPHER_STR:
        best_action = cellperso_to_cell(best_action)
    else:
        best_action = (
            cellperso_to_cell(best_action[0]),
            cellperso_to_cell(best_action[1]),
        )
    print(f"Action played by player {player} : {best_action}")
    return env, best_action


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ClientTesting", description="Test the IA02 python client"
    )

    parser.add_argument("group_id")
    parser.add_argument("members")
    parser.add_argument("password")
    #parser.add_argument("-s", "--server-url", default="http://localhost:8080/")
    parser.add_argument("-s", "--server-url", default="http://lchappuis.fr:8080/")
    parser.add_argument("-d", "--disable-dodo", action="store_true")
    parser.add_argument("-g", "--disable-gopher", action="store_true")
    args = parser.parse_args()

    available_games = [DODO_STR, GOPHER_STR]
    if args.disable_dodo:
        available_games.remove(DODO_STR)
    if args.disable_gopher:
        available_games.remove(GOPHER_STR)

    start(
        args.server_url,
        args.group_id,
        args.members,
        args.password,
        available_games,
        initialize,
        strategy,
        final_result,
        gui=True,
    )
