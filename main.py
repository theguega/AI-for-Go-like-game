import tools.game as gopher_dodo

if __name__ == "__main__":
    name = "Gopher"
    size = 10

    if name == "Dodo":
        initial_state = gopher_dodo.new_dodo(size)
    elif name == "Gopher":
        initial_state = gopher_dodo.new_gopher(size)

    env = gopher_dodo.initialize(name, initial_state, gopher_dodo.B, size, 50)

    while not env.final():
        if env.player == gopher_dodo.R:
            action = env.strategy_random()
        else:
            action = env.strategy_random()
        env = env.play(action)
    #env.plot()
    print(env.score())
