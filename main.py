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
    start_time = time.time()

    for i in range(nb_iteration):
        print("Simulation :",i)
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
                action = env.monte_carlo(1000)
            intermediate_time = time.time()

            print("Tour n°", tour, " : ", intermediate_time - start_time, "s")
            tour += 1
            env.play(action)
        #env.tmp_show() #affichage de chaque grille finale

        if env.score() == 100:
            victoire_rouge += 1
        elif env.score() == -100:
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
    print(
        "Avantage rouge par rapport au bleu :",
        round((victoire_rouge - victoire_bleu) / nb_iteration * 100),
        "%",
    )
    print("Taux de victoire rouge : ", round(victoire_rouge / nb_iteration * 100), "%")
    env.final_show() #affichage de la dernière grille finale

    # ---- Export des données lors des simulations sur serveur dans fichier text ----
    export = False

    if export:
        strat_rouge : str = "Random"
        strat_bleu : str = "Monte Carlo : 100 simu"
        if name == "Dodo":
            path = "docu/simulations_dodo.txt"
        elif name == "Gopher":
            path = "docu/simulations_gopher.txt"

        with open(path, "a") as file:
            file.write(
                f"Taille de la grille : {size}\n"
                f"Nombre d'itérations : {nb_iteration}\n"
                f"Stratégie du joueur rouge : {strat_rouge}\n"
                f"Stratégie du joueur bleu : {strat_bleu}\n"
                f"Victoire rouge : {victoire_rouge}\n"
                f"Victoire bleu : {victoire_bleu}\n"
                f"Taux de victoire rouge : {round(victoire_rouge / nb_iteration * 100)}%\n"
                f"Temps d'exécution : {end_time - start_time}s\n"
                f"\n\n\n\n\n"
            )
        file.close()
