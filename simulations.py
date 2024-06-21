"""Simulations local avec export des données dans un fichier texte"""

import cProfile
import pstats
import time
from client.gndclient import GOPHER_STR, DODO_STR, State, Player, Time, RED
from tools.game import GameGopher, GameDodo, Environment, new_dodo, empty_grid

# board settings
NAME = DODO_STR  # change the game here (GOPHER_STR or DODO_STR)

DODO_SIZE = 4
GOPHER_SIZE = 6

# game settings
DODO_DEPTH = 8
DODO_NB_SIMU = 4000

GOPHER_DEPTH = 10
GOPHER_NB_SIMU = 3500

# other settings
NB_ITERATION = 1
DISPLAY = False
EXPORT = True


def initialize_simu(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """
    Initialize the environment with the game, the state, the player, the hex_size and the total_time
    """
    if game == GOPHER_STR:
        env_gopher = GameGopher(game, state, player, hex_size, total_time)
        return env_gopher
    env_dodo = GameDodo(game, state, player, hex_size, total_time)
    return env_dodo


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    # ---- Boucle de jeu ----
    victoire_rouge: int = 0
    victoire_bleu: int = 0
    start_time = time.time()
    MEAN_SIMU_TIME = 0

    for i in range(NB_ITERATION):
        print("Simulation :", i)
        start_time_simu = time.time()
        if NAME == DODO_STR:
            SIZE = DODO_SIZE
            DEPTH = DODO_DEPTH
            SIMU = DODO_NB_SIMU
            initial_state = new_dodo(SIZE)
        else:
            SIZE = GOPHER_SIZE
            DEPTH = GOPHER_DEPTH
            SIMU = GOPHER_NB_SIMU
            initial_state = empty_grid(SIZE)

        env = initialize_simu(NAME, initial_state, RED, SIZE, 50)
        TOUR = 0

        while not env.final():
            debut_time_tour = time.time()
            if env.player == RED:
                # change strategy for RED player here
                # action = env.strategy_random()
                action = env.strategy_mc(SIMU)
                # action = env.strategy_alpha_beta(DEPTH)
                # action = env.strategy_alpha_beta_cache(DEPTH)
                if env.root:
                    for child in env.root.children:
                        if child.parent_action == action:
                            env.root = child
            else:
                # change strategy for BLUE player here
                # action = env.strategy_random()
                # action = env.strategy_mc(SIMU)
                action, env.root = env.strategy_mcts(SIMU,env.root)
                # action = env.strategy_alpha_beta(DEPTH)
                # action = env.strategy_alpha_beta_cache(DEPTH)

            fin_time_tour = time.time()
            print(
                "Joueur :",
                env.player,
                " | ",
                "Tour n°",
                TOUR,
                " : ",
                fin_time_tour - debut_time_tour,
                "s",
            )
            MEAN_SIMU_TIME += fin_time_tour - debut_time_tour
            TOUR += 1
            env.play(action)
            print()
            if DISPLAY:
                env.tmp_show()
        end_time_simu = time.time()

        if env.score() == 100:
            victoire_rouge += 1
        elif env.score() == -100:
            victoire_bleu += 1

        intermediate_time = time.time()
        print("Temps de simulation : ", end_time_simu - start_time_simu, "s")
        print("Winner :", "rouge" if env.score() == 100 else "bleu")
    MEAN_SIMU_TIME /= NB_ITERATION
    # ---- Affichage du profilage ----

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()
    end_time = time.time()
    print("Temps d'exécution : ", end_time - start_time, "s")

    # ---- Affichage de fin de partie ----
    print("---------------")
    print("Victoire rouge : ", victoire_rouge)
    print("Victoire bleu : ", victoire_bleu)
    print(
        "Avantage rouge par rapport au bleu :",
        round((victoire_rouge - victoire_bleu) / NB_ITERATION * 100),
        "%",
    )
    print("Taux de victoire rouge : ", round(victoire_rouge / NB_ITERATION * 100), "%")

    # ---- Export des données lors des simulations sur serveur dans fichier text ----
    if EXPORT:
        strat_rouge: str = "MC 400 simulations"
        strat_bleu: str = "MCTS 400 simulations"
        if NAME == GOPHER_STR:
            PATH = "doc/simulations_dodo.txt"
        else:
            PATH = "doc/simulations_gopher.txt"

        with open(PATH, "a", encoding="utf-8") as file:
            file.write(
                f"Taille de la grille : {SIZE}\n"
                f"Nombre d'itérations : {NB_ITERATION}\n"
                f"Stratégie du joueur rouge : {strat_rouge}\n"
                f"Stratégie du joueur bleu : {strat_bleu}\n"
                f"Victoire rouge : {victoire_rouge}\n"
                f"Victoire bleu : {victoire_bleu}\n"
                f"Taux de victoire rouge : {round(victoire_rouge / NB_ITERATION * 100)}%\n"
                f"Temps d'exécution : {end_time - start_time}s\n"
                f"Temps moyen par simulation : {MEAN_SIMU_TIME}s\n"
                f"\n\n\n\n\n"
            )
        file.close()
    if DISPLAY:
        env.final_show()
