import tools.game as gopher_dodo

if __name__ == "__main__":
    name = "Gopher"
    size = 4
    if name == "Dodo":
        initial_state = gopher_dodo.new_dodo(size)
    elif name == "Gopher":
        initial_state = gopher_dodo.new_gopher(size)

    env = gopher_dodo.initialize(name, initial_state, gopher_dodo.B, size, 50)

    while not env.final():
        if env.player == gopher_dodo.R:
            action = env.strategy_random()
        else:
            action = env.strategy_alpha_beta()
        # print("Action :", action)
        env = env.play(action)

    #env.plot()

    if env.score() == 1:
        print("Blue wins")
    elif env.score() == -1:
        print("Red wins")
