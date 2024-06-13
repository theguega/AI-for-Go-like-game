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
    pass

def cellperso_to_cell(cell : Cell_perso) -> Cell :
    pass

def state_to_stateperso(state : State) -> State_perso :
    pass

def stateperso_to_state(state: State_perso) -> State:
    pass

def initialize(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """
    Initialize the environment with the game, the state, the player, the hex_size and the total_time
    """
    state2 : State_perso = state_to_stateperso(state)
    if game == GOPHER_STR:
        env = GameGopher(game, state2, player, hex_size, total_time)
    elif game == DODO_STR:
        env = GameDodo(game, state2, player, hex_size, total_time)
    else:
        raise ValueError("game must be 'gopher' or 'dodo'")
    return env

def strategy(
    env: Environment, state: State, player: Player, time_left: Time
) -> tuple[Environment, Action]:
    state2 : State_perso = state_to_stateperso(state)
    env.state=state2
    env.player=player
    action = env.strategy_mc(400)
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
        strategy,
        final_result,
        gui=True,
    )