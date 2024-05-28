import tools.game as gopher_dodo
import cProfile
import pstats
import time

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    # ---- Boucle de jeu ----
    name = "Dodo"
    size = 4
    nb_iteration = 10
    victoire_rouge = 0
    victoire_bleu = 0
    start_time = time.time()


    for i in range(nb_iteration):
        if name == "Dodo":
            initial_state = gopher_dodo.new_dodo(size)
        elif name == "Gopher":
            initial_state = gopher_dodo.new_gopher(size)

        env = gopher_dodo.initialize(name, initial_state, gopher_dodo.R, size, 50)
        tour=0
        while not env.final():
            if env.player == gopher_dodo.R:
                action = env.strategy_alpha_beta()
            else:
                action = env.strategy_random()
            intermediate_time = time.time()
            print("Tour n°", tour, " : ", intermediate_time - start_time, "s")
            tour += 1
            env.play(action)
            #env.tmp_show()
        
        if env.score() == 1:
            victoire_rouge += 1
        elif env.score() == -1:
            victoire_bleu += 1

    # ---- Affichage du profilage ----

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()
    end_time = time.time()
    print("Temps d'exécution : ", end_time - start_time, "s")

    # ---- Affichage de fin de partie ----
    print("Victoire rouge : ", victoire_rouge)
    print("Victoire bleu : ", victoire_bleu)
    print("Avantage rouge par rapport au bleu :", round((victoire_rouge-victoire_bleu)/nb_iteration*100), "%")
    print("Taux de victoire rouge : ", round(victoire_rouge/nb_iteration*100), "%")
    env.final_show()
