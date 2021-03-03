#!/usr/local/bin/python3
# assign.py : Assign people to teams
#
# Code by: name IU ID
#
# Based on skeleton code by R. Shah and D. Crandall, January 2021
#
import copy
import sys
import time
from queue import PriorityQueue

USER_PREFERENCES = {}

class PriorityElement:
    def __init__(self, cost, groups):
        self.cost = cost
        self.groups = groups
    def __lt__(self, other):
        return self.cost < other.cost

class UserPreferences:
    def __init__(self, userid, teams, blocked):
        self.userid = userid
        self.team_size = len(teams.split("-"))
        self.ideal_team = teams.split("-")
        self.ideal_team = [i for i in self.ideal_team if i != "zzz"]
        self.blocked = [] if blocked == "_" else blocked.split(",")

def find_all_groups(userids):
    final_groups = []
    if len(userids) == 1:
        return [[[userids[0]]]]
    prev_groups = find_all_groups(userids[:len(userids) - 1])
    for group in prev_groups:
        for i in range(len(group)):
            if len(group[i]) > 2:
                continue
            new_group = copy.deepcopy(group)
            new_group[i].append(userids[len(userids) - 1])
            final_groups.append(new_group)
        new_group = copy.deepcopy(group)
        new_group.append([userids[len(userids) - 1]])
        final_groups.append(new_group)
    return final_groups

def calculate_cost(userid, user_group):
    team_size_cost = 1 if USER_PREFERENCES[userid].team_size != len(user_group) else 0
    missing_member_cost = len([member for member in USER_PREFERENCES[userid].ideal_team if member not in user_group])
    blocked_member_cost = len([member for member in USER_PREFERENCES[userid].blocked if member in user_group]) * 2
    return team_size_cost + missing_member_cost + blocked_member_cost

def get_user_groups(user_groups):
    return ["-".join(group) for group in user_groups]

def read_user_preferences(input_file):
    global USER_PREFERENCES

    with open(input_file) as file:
        for line in file:
            userid, team, blocked = line.strip().split(" ")
            USER_PREFERENCES[userid] = UserPreferences(userid, team, blocked)

def successors(state):
    new_states = []
    start_index = 0
    for i in range(len(state)-1, -1 ,-1):
        if len(state[i]) > 1:
            start_index = i
            break
    for i in range(start_index, len(state)):
        if len(state[i]) > 2:
            continue
        last_elem_index = [*USER_PREFERENCES.keys()].index(state[i][len(state[i]) - 1])
        for j in range(i+1, len(state)):
            if [*USER_PREFERENCES.keys()].index(state[j][0]) > last_elem_index:
                new_state = copy.deepcopy(state)
                new_state.pop(j)
                new_state[i].extend(state[j])
                new_states.append(new_state)

    return new_states

def check_visited(visited_states, current_state):
    for visited_state in visited_states:
        if sum([1 for group in current_state if group in visited_state]) == len(current_state):
            return True
    return False

def solver(input_file):
    """
    1. This function should take the name of a .txt input file in the format indicated in the assignment.
    2. It should return a dictionary with the following keys:
        - "assigned-groups" : a list of groups assigned by the program, each consisting of usernames separated by hyphens
        - "total-cost" : total cost (number of complaints) in the group assignment
    3. Do not add any extra parameters to the solver() function, or it will break our grading and testing code.
    4. Please do not use any global variables, as it may cause the testing code to fail.
    5. To handle the fact that some problems may take longer than others, and you don't know ahead of time how
       much time it will take to find the best solution, you can compute a series of solutions and then
       call "yield" to return that preliminary solution. Your program can continue yielding multiple times;
       our test program will take the last answer you 'yielded' once time expired.
    """
    visited_states = []

    global USER_PREFERENCES
    read_user_preferences(input_file)

    fringe = PriorityQueue()
    initial_groups = [[i] for i in USER_PREFERENCES.keys()]
    min_cost = sum([calculate_cost(i[0], i) for i in initial_groups])
    min_group = initial_groups
    min_state_number = 0

    yield ({"assigned-groups": get_user_groups(min_group), "total-cost": min_cost})

    fringe.put(PriorityElement(min_cost, initial_groups))

    total_state_count = 0
    while not fringe.empty():
        total_state_count += 1
        priority_elem:PriorityElement = fringe.get()

        for succ in successors(priority_elem.groups):
            if check_visited(visited_states, succ):
                pass
                # print("Duplicate state: " + str(succ) + " with predecessor: " + str(priority_elem.groups))
            else:
                visited_states.append(succ)

            # Match the count to know if all the states are being generated.
            succ_cost = sum([calculate_cost(i, group) for group in succ for i in group])
            if succ_cost < min_cost:
                min_cost = succ_cost
                min_group = succ
                min_state_number = total_state_count
                print("Min state number: " + str(total_state_count))
                yield({"assigned-groups": get_user_groups(min_group), "total-cost": min_cost})
            fringe.put(PriorityElement(succ_cost, succ))

    print("Total state count: " + str(total_state_count))
    print("Total distinct states: " + str(len(visited_states)))
    print("Min State search value: " + str(min_state_number))
    # print("Distinct states: " + "\n".join([str(state) for state in visited_states]))
    yield({"assigned-groups": get_user_groups(min_group), "total-cost": min_cost})

    all_groups = find_all_groups(['djcran','sahmaini','sulagaop','fanjun','nthakurd','vkvats'])

    for uni_gp in all_groups:
        if len([1 for gp in uni_gp if len(gp) > 1]) == 0:
            continue

        found = False
        for visited_state in visited_states:
            if sum([1 for group in uni_gp if group in visited_state]) == len(uni_gp):
                found = True
                break
        if not found:
            print("State not generated: " + str(uni_gp))
            break


    # # Simple example. First we yield a quick solution
    # yield({"assigned-groups": ["vibvats-djcran-zkachwal", "shah12", "vrmath"],
    #            "total-cost" : 12})
    #
    # # Then we think a while and return another solution:
    # time.sleep(10)
    # yield({"assigned-groups": ["vibvats-djcran-zkachwal", "shah12-vrmath"],
    #            "total-cost" : 10})
    #
    # # This solution will never befound, but that's ok; program will be killed eventually by the
    # #  test script.
    # while True:
    #     pass
    #
    # yield({"assigned-groups": ["vibvats-djcran", "zkachwal-shah12-vrmath"],
    #            "total-cost" : 9})

if __name__ == "__main__":
    if(len(sys.argv) != 2):
        raise(Exception("Error: expected an input filename"))

    for result in solver(sys.argv[1]):
        print("----- Latest solution:\n" + "\n".join(result["assigned-groups"]))
        print("\nAssignment cost: %d \n" % result["total-cost"])
    
