#!/usr/local/bin/python3
# solver2021.py : 2021 Sliding tile puzzle solver
#
# Code by: radverma@iu.edu
#
# Based on skeleton code by D. Crandall, January 2021
#

import sys
from queue import PriorityQueue

ROWS=4
COLS=5

def printable_board(board):
    return "\n".join([ ('%3d ')*COLS  % board[j:(j+COLS)] for j in range(0, ROWS*COLS, COLS) ])

compare_count = {0:0,1:0,2:0,3:0,4:0,5:0,6:0}

class FringeItem:
    def __init__(self, data, priority):
        self.data = data
        self.priority = priority
    def __lt__(self, other):
        if type(self.priority) is not tuple:
            return self.priority < other.priority
        for i in range(len(self.priority)):
            if self.priority[i] != other.priority[i]:
                compare_count[i] += 1
                return self.priority[i] < other.priority[i]

        compare_count[len(self.priority)] += 1
        return True

def shift(state, cells):
    temp = state[cells[0]]
    for i in range(len(cells) - 1):
        state[cells[i]] = state[cells[i+1]]
    state[cells[len(cells) -1]] = temp
    return state

def shift_left(state, row_num):
    return shift(state[:], list(range(row_num * COLS, (row_num+1)*COLS)))

def shift_right(state, row_num):
    return shift(state[:], list(range((row_num+1) * COLS - 1, row_num * COLS - 1, -1)))

def shift_up(state, col_num):
    return shift(state[:], list(range(col_num, ROWS*COLS + col_num, COLS)))

def shift_down(state, col_num):
    return shift(state[:], list(range((ROWS-1)*COLS + col_num, col_num-1, -COLS)))

# return a list of possible successor states
def successors(state):
    states = []
    for i in range(ROWS):
        if i%2 == 0:
            states.append((shift_left(state, i), "L"+str(i+1)))
        else:
            states.append((shift_right(state, i), "R" + str(i+1)))

    for i in range(COLS):
        if i%2 == 0:
            states.append((shift_up(state, i), "U" + str(i+1)))
        else:
            states.append((shift_down(state, i), "D" + str(i+1)))

    return states

def cell_num(i, j):
    return i*COLS + j

# check if we've reached the goal
def is_goal(state):
    return all([state[i] == i+1 for i in range(ROWS * COLS)])

def get_cell_from_index(index):
    return (int(index/COLS), index%COLS)

def get_manhatten_distance(cell1, cell2):
    # TODO: Validate this logic
    if cell1 == cell2:
        return 0

    cell1 = get_cell_from_index(cell1)
    cell2 = get_cell_from_index(cell2)

    if cell1[1] % 2 == 0:
        if cell2[0] > cell1[0]:
            row_distance = cell1[0] + ROWS - cell2[0]
        else:
            row_distance = cell1[0] - cell2[0]
    else:
        if cell2[0] >= cell1[0]:
            row_distance = cell2[0] - cell1[0]
        else:
            row_distance = cell2[0] + ROWS - cell1[0]

    if cell2[0] % 2 == 0:
        if cell2[1] > cell1[1]:
            col_distance = cell1[1] + COLS - cell2[1]
        else:
            col_distance = cell1[1] - cell2[1]
    else:
        if cell2[1] >= cell1[1]:
            col_distance = cell2[1] - cell1[1]
        else:
            col_distance = cell2[1] + COLS - cell1[1]

    min_distance = row_distance + col_distance

    if cell1[0] % 2 == 0:
        if cell2[1] > cell1[1]:
            col_distance = cell1[1] + COLS - cell2[1]
        else:
            col_distance = cell1[1] - cell2[1]
    else:
        if cell2[1] >= cell1[1]:
            col_distance = cell2[1] - cell1[1]
        else:
            col_distance = cell2[1] + COLS - cell1[1]

    if cell2[1] % 2 == 0:
        if cell2[0] > cell1[0]:
            row_distance = cell1[0] + ROWS - cell2[0]
        else:
            row_distance = cell1[0] - cell2[0]
    else:
        if cell2[0] >= cell1[0]:
            row_distance = cell2[0] - cell1[0]
        else:
            row_distance = cell2[0] + ROWS - cell1[0]

    return min(min_distance, row_distance + col_distance)

    # return min(abs(cell1[0] - cell2[0]), (min(cell1[0],cell2[0]) + ROWS - max(cell1[0],cell2[0])))\
    #        + min(abs(cell1[1] - cell2[1]), (min(cell1[1],cell2[1]) + COLS - max(cell1[1],cell2[1])))

def get_mismatches_for_cell(state, index):
    elem = state[index]
    col_mismatches = row_mismatches = 0
    (row, col) = get_cell_from_index(index)

    if elem % ROWS not in [0,1]:
        if (elem-1) != state[cell_num(row, get_cell_from_index(index-1)[1])]:
            row_mismatches += 1
        if (elem+1) != state[cell_num(row, get_cell_from_index(index+1)[1])]:
            row_mismatches += 1
    elif elem % ROWS == 0:
        if (elem-1) != state[cell_num(row, get_cell_from_index(index-1)[1])]:
            row_mismatches += 1
        if (cell_num(row, col) + 2) != state[cell_num(row, get_cell_from_index(index+1)[1])]:
            row_mismatches += 1

    if (elem-COLS) != state[(index - COLS) % (ROWS*COLS)]:
        col_mismatches += 1
    if (elem+COLS) != state[(index + COLS) % (ROWS*COLS)]:
        col_mismatches += 1

    return (row_mismatches, col_mismatches)

def get_total_mismatches(state):
    return sum([sum(get_mismatches_for_cell(state, i)) for i in range(ROWS * COLS)])

def get_mismatch_coefficient(state):
    col_mismatches = row_mismatches = 0
    for i in range(ROWS * COLS):
        mismatches = get_mismatches_for_cell(state, i)
        row_mismatches += mismatches[0]
        col_mismatches += mismatches[1]

    return col_mismatches / (ROWS*2) + row_mismatches / (COLS*2)

higher_counts = 0

def get_h(state):
    global higher_counts
    manhatn =  max([get_manhatten_distance(i, state[i] - 1) for i in range(len(state))])
    # mismatches = get_mismatch_coefficient(state)

    # if manhatn > mismatches:
    #     higher_counts +=1
    # else:
    #     higher_counts -=1

    return manhatn

def get_max_distance_node_count(state):
    max_count = 0
    max_distance = 0
    for i in range(ROWS * COLS):
        dist = get_manhatten_distance(i, state[i] - 1)
        if dist > max_distance:
            max_distance = dist
            max_count = 1
        elif dist == max_distance:
            max_count += 1
    return max_count

def solve(initial_board):
    """
    1. This function should return the solution as instructed in assignment, consisting of a list of moves like ["R2","D2","U1"].
    2. Do not add any extra parameters to the solve() function, or it will break our grading and testing code.
       For testing we will call this function with single argument(initial_board) and it should return 
       the solution.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """

    if type(initial_board[0]) is list:
        initial_board = [j for i in initial_board for j in i]

    que = PriorityQueue()

    # que.put((0, 0,initial_board, ""))
    que.put(FringeItem((0, initial_board, ""), (0, 0)))

    state_count = 1

    total_hs = 0
    count_hs = 0
    max_hs = 0
    min_hs = 500
    total_for_loop = 0

    while not que.empty():

        if count_hs%1000 == 400:
            print("Higher counts: " + str(higher_counts))
            print("for loop counts: " + str(total_for_loop))
            print("max_hs: " + str(max_hs))
            print("min_hs: " + str(min_hs))
            print("avg_hs: " + str(total_hs/count_hs))
            print("compare stats: " + str(compare_count))

        state_count = state_count + 1

        fringe_item = que.get()
        elem = fringe_item.data
        if is_goal(elem[1]):
            if elem[2] == '':
                return []
            print("Total states visited: " + str(state_count))
            return elem[2].strip().split(" ")
        for succ in successors(elem[1]):
            total_for_loop += 1
            a=get_h(succ[0])
            count_hs+=1
            total_hs+=a
            max_hs=max(a,max_hs)
            min_hs=min(a,min_hs)

            fs = a + elem[0]
            # que.put((fs, fs, succ[0], elem[3] + " " + succ[1]))
            que.put(FringeItem((elem[0] + 1, succ[0], elem[2] + " " + succ[1]), (elem[0] + 1 + a, get_total_mismatches(succ[0]))))

def make_move(state, move):
    dir = move[0]
    num = int(move[1:]) - 1
    if dir == 'L':
        return shift_left(state, num)
    if dir == 'R':
        return shift_right(state, num)
    if dir == 'D':
        return shift_down(state, num)
    if dir == 'U':
        return shift_up(state, num)

def make_moves(state, moves):
    moves = moves.split(" ")
    for move in moves:
        state = make_move(state, move)
        # print("--------------------")
        # print(printable_board(tuple(state)))
    return state

# Please don't modify anything below this line
#
if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected a board filename"))

    start_state = []
    with open(sys.argv[1], 'r') as file:
        for line in file:
            start_state += [ int(i) for i in line.split() ]

    if len(start_state) != ROWS*COLS:
        raise(Exception("Error: couldn't parse start state file"))

    print("Start state: \n" +printable_board(tuple(start_state)))

    print("Solving...")

    # start_state = make_moves(start_state, "D2 D2 D2 R2 R2 R2 R2 L4 R1 L2 D3 D3 U4 R3 L2 R3 L4 D5")
    # start_state = make_moves(start_state, "D2 D2 D2 R2 R2 R2 R2 R1 D1 D5 L4 U2 L2 D3 R3 D3 U4 L2 R3")
    # start_state = make_moves(start_state, "D2 D2 D2 R2 R2 R2 R2 R3 D3 U4 L2 R3 R1 D1 D5 L4 U2 L2 D3")

    print(printable_board(tuple(start_state)))

    route = solve(start_state)

    print("Solution found in " + str(len(route)) + " moves:" + "\n" + " ".join(route))
