import tools.game as gopher_dodo
import cProfile
import pstats

if __name__ == "__main__":
    profiler = cProfile.Profile()
    profiler.enable()

    # ---- Boucle de jeu ----
    name = "Gopher"
    size = 10
    nb_iteration = 100

    for i in range(nb_iteration):
        if name == "Dodo":
            initial_state = gopher_dodo.new_dodo(size)
        elif name == "Gopher":
            initial_state = gopher_dodo.new_gopher(size)

        env = gopher_dodo.initialize(name, initial_state, gopher_dodo.R, size, 50)
        while not env.final():
            if env.player == gopher_dodo.R:
                action = env.strategy_random()
            else:
                action = env.strategy_random()
            env.play(action)

    """
    if env.score() == 1:
        print("Red wins")
    elif env.score() == -1:
        print("Blue wins")
    """

    # ---- Affichage du profilage ----

    profiler.disable()
    stats = pstats.Stats(profiler).sort_stats("tottime")
    stats.print_stats()

    # ---- Affichage du plateau en fin de partie ----
    #env.plot()
