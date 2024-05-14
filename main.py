import tools.game as game


def main():
    # plot gopher and dodo on 2 different figures
    size_0 = 6
    empty_goph = game.new_gopher(size_0)
    goph = game.initialize("Gopher", empty_goph, game.R, size_0, 1000)
    #goph.plot()

    size_1 = 6
    empty_dodo = game.new_dodo(size_1)
    dodo = game.initialize("Dodo", empty_dodo, game.B, size_1, 1000)
    dodo.plot()

if __name__ == "__main__":
    main()
