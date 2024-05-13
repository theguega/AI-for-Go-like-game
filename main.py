import tools.board as board


def main():
    #plot gopher and dodo on 2 different figures
    dodo = board.initialize_dodo("dodo", {}, board.R, 5, 10)
    dodo.plot()

    gopher = board.initialise_gopher("gopher", {}, board.B, 5, 10)
    gopher.plot()




if __name__ == "__main__":
    main()
