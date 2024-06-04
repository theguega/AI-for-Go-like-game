import tools.game as gopher_dodo
from tools.mcts import *
import cProfile
import pstats
import time


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    # ---- Boucle de jeu ----
    name = "Gopher"
    size = 8
    nb_iteration = 1
    victoire_rouge = 0
    victoire_bleu = 0
    for i in range(nb_iteration):
        start_time = time.time()
        if name == "Dodo":
            initial_state = gopher_dodo.new_dodo(size)
        elif name == "Gopher":
            initial_state = gopher_dodo.new_gopher(size)

        env = gopher_dodo.initialize(name, initial_state, gopher_dodo.R, size, 50)
        tour = 0
        root:MCTSNode = None
        while not env.final():
            if env.player == gopher_dodo.R:
                action = env.strategy_random()
                if root:
                    for child in root.children:
                        if child.parent_action == action:
                            root = child
            else:
                action,root = env.strategy_mcts(200,root=root)

            intermediate_time = time.time()
            print("Tour n°", tour, " : ", intermediate_time - start_time, "s")
            tour += 1
            env.play(action)
        env.final_show()

        if env.score() == 100:
            victoire_rouge += 1
        elif env.score() == -100:
            victoire_bleu += 1

        intermediate_time = time.time()
        print(intermediate_time - start_time)
        print("Winner :", "rouge" if env.score() == 100 else "bleu")
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