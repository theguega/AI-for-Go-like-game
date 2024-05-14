import tools.board as board


def main():
    # plot gopher and dodo on 2 different figures
    b = board.initialize("Dodo", {}, board.R, 5, 10)
    b.plot()


if __name__ == "__main__":
    main()
