#######################################################################
#######################################################################
##############                                       ##################
#############       FICHIER A LANCER POUR SERVEUR     #################
##############                                       ##################
#######################################################################
#######################################################################
import argparse
from client.gndclient import start, Action, Score, Player, State, Time, DODO_STR, GOPHER_STR
from tools.game import *


def cell_to_cellperso(cell : Cell) -> Cell_perso :
    # convert from tuple[int, int] to Hex
    return axial_to_cube(DoubledCoord(cell[0], cell[1]))

def cellperso_to_cell(cell : Cell_perso) -> Cell :
    # convert from Hex to tuple[int, int]
    return (cell.q, cell.r)


def get_action(env : Environment, new_state : State) -> Action :
    # compare new state of the game with state store in the environment to get the action played by the opponent
    if env.game == GOPHER_STR:
        # find the cell that appaered in the new state
        for pos,player in new_state:
            if player != EMPTY:
                hex = cell_to_cellperso(pos)
                if env.state[hex] == EMPTY:
                    return hex
        return None
    elif env.game == DODO_STR:
        # find the cell that appeard in the new state
        destination = None
        for pos,player in new_state:
            if player != EMPTY:
                hex = cell_to_cellperso(pos)
                if env.state[hex] == EMPTY:
                    destination = pos
                    break
        #find the cell that dissapeard in the old state
        source = None
        for hex, player in env.state.items():
            if player != EMPTY:
                pos = cellperso_to_cell(hex)
                for cell2, player2 in new_state:
                    if player2 == EMPTY:
                        if pos == cell2:
                            source = pos
                            break
        if source is None or destination is None:
            return None
        else :
            return (source,destination)

def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    #create a new env
    if game == GOPHER_STR:
        initial_state : State_perso = new_gopher(hex_size)
        env = GameGopher(game, initial_state, player, hex_size, total_time)
    elif game == DODO_STR:
        initial_state : State_perso = new_dodo(hex_size)
        env = GameDodo(game, initial_state, player, hex_size, total_time)
    
    # if player is BLUE, we need to get the first action of the opponent
    if player == BLUE:
        action = get_action(env, state)
        env.play(action)

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
    action_opponent = get_action(env, state)
    print("Action opponent : ", action_opponent)
    if action_opponent is not None:
        env.play(action_opponent)

    nb_simu : int = 400
    action = env.strategy_mc(nb_simu)
    print("Action played : ", action)
    env.play(action)

    return env, action

def strategy_mcts(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)

    nb_simu : int = 400
    action, _ = env.strategy_mcts(nb_simu)
    env.play(action)
    
    return env, action

def strategy_negascoot(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)

    depth : int = 6
    if player == BLUE:
        depth += 1
    action = env.strategy_negascout(depth)
    env.play(action)

    return env, action

def strategy_alphabeta(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)

    depth : int = 6
    if player == BLUE:
        depth += 1
    action = env.strategy_alpha_beta(depth)
    env.play(action)

    return env, action

def strategy_random(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    action_opponent = get_action(env, state)
    if action_opponent is not None:
        env.play(action_opponent)

    action = env.strategy_random()
    env.play(action)

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
    parser.add_argument("-d", "--disable-dodo", action="store_false")
    parser.add_argument("-g", "--disable-gopher", action="store_false")
    args = parser.parse_args()

    available_games = []
    if not args.disable_dodo:
        available_games.append(DODO_STR)
    if not args.disable_gopher:
        available_games.append(GOPHER_STR)

    start(
        args.server_url,
        args.group_id,
        args.members,
        args.password,
        available_games,
        initialize,
        strategy_mc, #change strategy here
        final_result,
        gui=True,
    )