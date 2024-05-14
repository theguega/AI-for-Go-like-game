from pprint import pprint
from typing import *

Grid = List[List[int]]
EMPTY = 0
R = 1
B = 2
def create_empty_grid(side_size:int) -> Grid:
    mat = list()
    for i in range(side_size-1):
        line = list()
        for j in range(side_size-i-1):
            line.append(3)
        for j in range(side_size-i-1,(side_size*2-1)):
            line.append(EMPTY)
        mat.append(line)
    for i in range(side_size):
        line = list()
        for j in range(side_size*2-1-i):
            line.append(EMPTY)
        for j in range(side_size*2-1-i,side_size*2-1):
            line.append(3)
        mat.append(line)
    return mat

def init_dodo(side_size:int)->Grid:
    grid = create_empty_grid(side_size)
    for i in range(side_size):
        for j in range(side_size+i-1,side_size*2-1):
            grid[i][j] = R
    for i in range(side_size-1,side_size*2-1):
        for j in range(i-side_size+2):
            grid[i][j] = B
    return grid




if __name__ == '__main__':
    pprint(init_dodo(7))
