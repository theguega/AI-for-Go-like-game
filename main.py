#######################################################################
#######################################################################
##############                                       ##################
#############       FICHIER A LANCER POUR SERVEUR     #################
##############                                       ##################
#######################################################################
#######################################################################
import argparse
from client.gndclient import (
    start,
    Action,
    Score,
    Player,
    State,
    Time,
    DODO_STR,
    GOPHER_STR,
)
from tools.game import *

SIMU_GOPHER = 5000
SIMU_DODO = 1500
DEPTH_GOPHER = 6
DEPTH_DODO = 6


def cell_to_cellperso(cell: Cell) -> Cell_perso:
    # convert from tuple[int, int] to Hex
    return axial_to_cube(DoubledCoord(cell[0], cell[1]))


def cellperso_to_cell(cell: Cell_perso) -> Cell:
    # convert from Hex to tuple[int, int]
    return (cell.q, cell.r)


def get_action(env: Environment, new_state: State) -> Action:
    # compare new state of the game with state store in the environment to get the action played by the opponent
    if env.game == GOPHER_STR:
        # find the cell that appaered in the new state
        for pos, player in new_state:
            if player != EMPTY:
                hex = cell_to_cellperso(pos)
                if env.state[hex] == EMPTY:
                    return hex
        return None
    elif env.game == DODO_STR:
        # find the cell that dissapeard in the old state
        source = None
        for hex, player in env.state.items():
            if player != EMPTY:
                pos = cellperso_to_cell(hex)
                for cell2, player2 in new_state:
                    if player2 == EMPTY:
                        if pos == cell2:
                            source = hex
                            break

        # find the cell that appeard in the new state
        destination = None
        for pos, player in new_state:
            if player != EMPTY:
                hex = cell_to_cellperso(pos)
                if env.state[hex] == EMPTY:
                    destination = hex
                    break
        if source is None or destination is None:
            return None
        else:
            return (source, destination)


"""
def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    #create a new env
    if game == GOPHER_STR:
        initial_state : State_perso = empty_grid(hex_size)
        env = GameGopher(game, initial_state, player, hex_size, total_time)
    elif game == DODO_STR:
        initial_state : State_perso = new_dodo(hex_size)
        env = GameDodo(game, initial_state, player, hex_size, total_time)

    # if player is BLUE, we need to get the first action of the opponent
    if player == BLUE and game == GOPHER_STR:
        action = get_action(env, state)
        env.play(action)

    return env
"""


def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    # create a new env
    initial_state: State_perso = empty_grid(hex_size)
    if game == GOPHER_STR:
        env = GameGopher(game, initial_state, player, hex_size, total_time)
        # synchronize the state of the game with the state given by the server
        for pos, player in state:
            hex = cell_to_cellperso(pos)
            env.state[hex] = player
            if player == RED:
                env.red_pawns[hex] = RED
            elif player == BLUE:
                env.blue_pawns[hex] = BLUE

    elif game == DODO_STR:
        env = GameDodo(game, initial_state, player, hex_size, total_time)
        # synchronize the state of the game with the state given by the server
        for pos, player in state:
            hex = cell_to_cellperso(pos)
            env.state[hex] = player
            if player == RED:
                env.red_pawns.append(hex)
            elif player == BLUE:
                env.blue_pawns.append(hex)
    return env


def strategy_brain(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    print("New state ", state)
    print("Time remaining ", time_left)
    print("What's your play ? ", end="")
    s = input()
    print()
    t = ast.literal_eval(s)
    return (env, t)


def strategy_mc(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    print(f"Time remaining for player {player} : {time_left}")

    # update the env with the action of the opponent
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)

    # action to play
    nb_simu: int = SIMU_GOPHER if env.game == GOPHER_STR else SIMU_DODO
    action = env.strategy_mc(nb_simu)
    env.play(action)

    # convert the action for the api
    if env.game == GOPHER_STR:
        action = cellperso_to_cell(action)
    elif env.game == DODO_STR:
        action = (cellperso_to_cell(action[0]), cellperso_to_cell(action[1]))

    return env, action


def strategy_mcts(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    print(f"Time remaining for player {player} : {time_left}")

    # update the env with the action of the opponent
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)
        # TO-DO : MANAGE ROOT CREATION

    # action to play
    nb_simu: int = SIMU_GOPHER if env.game == GOPHER_STR else SIMU_DODO
    action, _ = env.strategy_mcts(nb_simu)
    env.play(action)

    # convert the action for the api
    if env.game == GOPHER_STR:
        action = cellperso_to_cell(action)
    elif env.game == DODO_STR:
        action = (cellperso_to_cell(action[0]), cellperso_to_cell(action[1]))

    return env, action


def strategy_negascoot(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    print(f"Time remaining for player {player} : {time_left}")

    # update the env with the action of the opponent
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)

    # action to play
    depth: int = DEPTH_GOPHER if env.game == GOPHER_STR else DEPTH_DODO
    if player == BLUE:
        depth += 1
    action = env.strategy_negascout(depth)
    env.play(action)

    # convert the action for the api
    if env.game == GOPHER_STR:
        action = cellperso_to_cell(action)
    elif env.game == DODO_STR:
        action = (cellperso_to_cell(action[0]), cellperso_to_cell(action[1]))

    return env, action


def strategy_alphabeta(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    print(f"Time remaining for player {player} : {time_left}")

    # update the env with the action of the opponent
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)

    # action to play
    depth: int = DEPTH_GOPHER if env.game == GOPHER_STR else DEPTH_DODO
    if player == BLUE:
        depth += 1
    action = env.strategy_alpha_beta(depth)
    env.play(action)

    # convert the action for the api
    if env.game == GOPHER_STR:
        action = cellperso_to_cell(action)
    elif env.game == DODO_STR:
        action = (cellperso_to_cell(action[0]), cellperso_to_cell(action[1]))

    return env, action


def strategy_random(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    print(f"Time remaining for player {player} : {time_left}")

    # update the env with the action of the opponent
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)

    # action to play
    action = env.strategy_random()
    env.play(action)

    # convert the action for the api
    if env.game == GOPHER_STR:
        action = cellperso_to_cell(action)
    elif env.game == DODO_STR:
        action = (cellperso_to_cell(action[0]), cellperso_to_cell(action[1]))

    return env, action


def final_result(state: State, score: Score, player: Player):
    print(f"Ending: {player} wins with a score of {score}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        prog="ClientTesting", description="Test the IA02 python client"
    )

    parser.add_argument("group_id")
    parser.add_argument("members")
    parser.add_argument("password")
    parser.add_argument("-s", "--server-url", default="http://localhost:8080/")
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
        strategy_mc,
        final_result,
        gui=True,
    )
