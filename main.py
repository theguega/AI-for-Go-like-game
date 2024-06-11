import tools.game as gopher_dodo
from tools.mcts import *
import cProfile
import pstats
import time


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    # ---- Boucle de jeu ----
    name = "Dodo"
    size = 4
    nb_iteration = 1
    victoire_rouge = 0
    victoire_bleu = 0
    start_time = time.time()
    mean_simu_time = 0

    for i in range(nb_iteration):
        print("Simulation :", i)
        start_time_simu = time.time()
        if name == "Dodo":
            initial_state = gopher_dodo.new_dodo(size)
        elif name == "Gopher":
            initial_state = gopher_dodo.new_gopher(size)

        env = gopher_dodo.initialize(name, initial_state, gopher_dodo.R, size, 50)
        tour = 0
        root: MCTSNode = None  # mcts root node

        while not env.final():
            debut_time_tour = time.time()
            if env.player == gopher_dodo.R:
                action, root = env.strategy_mcts(1000, root=root)
                #action = env.strategy_random()
            else:
                action = env.strategy_mc(1000)
                # for the mcts, we need to update the root node
                if root:
                    for child in root.children:
                        if child.parent_action == action:
                            root = child

            fin_time_tour = time.time()
            print("Joueur :",env.player," | ", "Tour n°", tour, " : ", fin_time_tour-debut_time_tour, "s")
            mean_simu_time += fin_time_tour-debut_time_tour
            tour += 1
            env.play(action)
            print()
        end_time_simu = time.time()

        if env.score() == 100:
            victoire_rouge += 1
        elif env.score() == -100:
            victoire_bleu += 1

        intermediate_time = time.time()
        print("Temps de simulation : ", end_time_simu - start_time_simu, "s")
        print("Winner :", "rouge" if env.score() == 100 else "bleu")
    mean_simu_time /= nb_iteration
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
        round((victoire_rouge - victoire_bleu) / nb_iteration * 100),
        "%",
    )
    print("Taux de victoire rouge : ", round(victoire_rouge / nb_iteration * 100), "%")

    env.final_show()
