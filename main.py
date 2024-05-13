import tools.board as board


def main():
    # plot gopher and dodo on 2 different figures
    board = board.initialize("Gopher", {}, board.R, 5, 10)
    board.plot()


if __name__ == "__main__":
    main()
