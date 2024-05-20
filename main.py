import tools.game as gopher_dodo
import pprint

if __name__ == "__main__":
    name = "Dodo"
    size = 4
    if name == "Dodo":
        initial_state = gopher_dodo.new_dodo(size)
    elif name == "Gopher":
        initial_state = gopher_dodo.new_gopher(size)

    env = gopher_dodo.initialize(name, initial_state, gopher_dodo.B, size, 50)
    env.plot()
    tour = 0
    while not env.final():
        print(f"tour : {tour}; joueur : {env.player}")
        tour +=1
        if env.player == gopher_dodo.R:
            action = env.strategy_random()
        else:
            action = env.strategy_alpha_beta()

        print("Action :", action)
        env = env.play(action)
        env.plot()

    if env.score() == 1:
        print("Blue wins")
    elif env.score() == -1:
        print("Red wins")
