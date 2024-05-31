import tools.game as gopher_dodo
import cProfile
import pstats
import time


if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    # ---- Boucle de jeu ----
    name = "Gopher"
    size = 5
    nb_iteration = 100
    victoire_rouge = 0
    victoire_bleu = 0

    error = 0
    errors = {}
    for i in range(nb_iteration):
        start_time = time.time()
        print(f"Iteration {i}/{nb_iteration}")
        if name == "Dodo":
            initial_state = gopher_dodo.new_dodo(size)
        elif name == "Gopher":
            initial_state = gopher_dodo.new_gopher(size)

        env = gopher_dodo.initialize(name, initial_state, gopher_dodo.R, size, 50)
        tour = 0

        while not env.final():
            if env.player == gopher_dodo.R:
                action = env.strategy_random()
            else:
                action = env.strategy_mcts(1000)


            #print("Tour n°", tour, " : ", intermediate_time - start_time, "s")
            #print("Joueur", env.player, "Action", action, "")
            tour += 1
            env.play(action)
        #env.tmp_show()

        if env.score() == 100:
            victoire_rouge += 1
        elif env.score() == -100:
            victoire_bleu += 1
        #env.final_show()
        # except Exception as e:
        #     error +=1
        #     if str(e) in errors.keys():
        #         errors[str(e)] += 1
        #     else:
        #         errors[str(e)] = 1
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
    print("Erreurs: \n",errors)
    print("Victoire rouge : ", victoire_rouge)
    print("Victoire bleu : ", victoire_bleu)
    print(
        "Avantage rouge par rapport au bleu :",
        round((victoire_rouge - victoire_bleu) / nb_iteration * 100),
        "%",
    )
    print("Taux de victoire rouge : ", round(victoire_rouge / nb_iteration * 100), "%")
    #env.final_show()
