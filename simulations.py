#######################################################################
#######################################################################
##############                                       ##################
#############       CE FICHIER IMPLEMENTE NOTRE       #################
##############      NOTRE BOUCLE DE JEUX PERSO       ##################
##############                                       ##################
#######################################################################
#######################################################################
import cProfile
import pstats
import time

from client.gndclient import *
from tools.game import *

# board settings
NAME = GOPHER_STR
SIZE = 4

# game settings
NB_ITERATION = 50
BASE_DEPTH = 6 # depth for alphabeta algorythms
NB_SIMU = 400 # number of simulations for monte carlo algorythms

# other settings
DISPLAY = False
EXPORT = True

def initialize_simu(
    game: str, state: State, player: Player, hex_size: int, total_time: Time
) -> Environment:
    """
    Initialize the environment with the game, the state, the player, the hex_size and the total_time
    """
    if game == GOPHER_STR:
        env = GameGopher(game, state, player, hex_size, total_time)
    elif game == DODO_STR:
        env = GameDodo(game, state, player, hex_size, total_time)
    else:
        raise ValueError("game must be 'Gopher' or 'Dodo'")
    return env



if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    # ---- Boucle de jeu ----
    victoire_rouge = 0
    victoire_bleu = 0
    start_time = time.time()
    mean_simu_time = 0

    for i in range(NB_ITERATION):
        print("Simulation :", i)
        start_time_simu = time.time()
        if NAME == DODO_STR:
            initial_state = new_dodo(SIZE)
        elif NAME == GOPHER_STR:
            initial_state = empty_grid(SIZE)

        env = initialize_simu(NAME, initial_state, RED, SIZE, 50)
        tour = 0

        while not env.final():
            debut_time_tour = time.time()
            if env.player == RED:
                depth = BASE_DEPTH
                
                action, _ = env.strategy_mcts(NB_SIMU)  #change strategy for RED player here
                # action = env.strategy_alpha_beta(depth) #change strategy for RED player here
                # action = env.strategy_mc(NB_SIMU) #change strategy for RED player here
            else:
                depth = BASE_DEPTH+1

                action = env.strategy_alpha_beta(depth) #change strategy for BLUE player here
                # action = env.strategy_mc(NB_SIMU) #change strategy for BLUE player here
                # action, _ = env.strategy_mcts(NB_SIMU) #change strategy for BLUE player here

            fin_time_tour = time.time()
            print(
                "Joueur :",
                env.player,
                " | ",
                "Tour n°",
                tour,
                " : ",
                fin_time_tour - debut_time_tour,
                "s",
            )
            mean_simu_time += fin_time_tour - debut_time_tour
            tour += 1
            env.play(action)
            print()
            if DISPLAY:
                env.final_show()
        end_time_simu = time.time()

        if env.score() == 100:
            victoire_rouge += 1
        elif env.score() == -100:
            victoire_bleu += 1

        intermediate_time = time.time()
        print("Temps de simulation : ", end_time_simu - start_time_simu, "s")
        print("Winner :", "rouge" if env.score() == 100 else "bleu")
    mean_simu_time /= NB_ITERATION
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
        if NAME == "Dodo":
            path = "doc/simulations_dodo.txt"
        elif NAME == "Gopher":
            path = "doc/simulations_gopher.txt"

        with open(path, "a") as file:
            file.write(
                f"Taille de la grille : {SIZE}\n"
                f"Nombre d'itérations : {NB_ITERATION}\n"
                f"Stratégie du joueur rouge : {strat_rouge}\n"
                f"Stratégie du joueur bleu : {strat_bleu}\n"
                f"Victoire rouge : {victoire_rouge}\n"
                f"Victoire bleu : {victoire_bleu}\n"
                f"Taux de victoire rouge : {round(victoire_rouge / NB_ITERATION * 100)}%\n"
                f"Temps d'exécution : {end_time - start_time}s\n"
                f"Temps moyen par simulation : {mean_simu_time}s\n"
                f"\n\n\n\n\n"
            )
        file.close()
    
    if DISPLAY:
        env.final_show()
