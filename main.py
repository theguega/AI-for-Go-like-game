import tools.board as board

def main():
    b = board.initialize_dodo("Dodo", {}, 1, 4, 1000)
    b.plot()

if __name__ == "__main__":
    main()