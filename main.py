import tools.game as game


def main():
    # plot gopher and dodo on 2 different figures
    b = game.initialize("Dodo", {}, game.R, 6, 1000)
    b.plot()

if __name__ == "__main__":
    main()
