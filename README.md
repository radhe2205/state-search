# Part 1
1. Problem Formulation:
   a. State space: 4x5 board with 20 tiles numbered 1-20
   b. Successor function: Any legal move of a row or columns (1st, 3rd, and 5th column slide up, 2nd and 4th columns slide down, 1st and 3rd rows slide left, and 2nd and 4th rows
                          slide right)
   c. Edge weights: Each move of a tile has a cost of 1.
   d. Heuristic function: The heuristic being used to assign a priority to the successors in the priority queue, is the maximum of the minimum moves required for a tile to reach
                          its goal state. The states with the lowest h(s) are given highest priority.
2. How it works:
3. Problems faced and design decisions:

# Part 2
1. Problem Formulation:
  a. State space: Map of cities and highways
  b. Successor function: Path connecting current location to next location
  c. Edge weights: The weights depends on the user's choice of cost function of either number of road segments, total distance, fastest route, or safest route. 
  d. Heuristic function: If two successor states have the same cost, then a heuristic is used to determine which successor has a smaller distance to the goal city based on
                         the difference between latitude and longitude. The successor with the smaller distance is the one chosen by the agent. 
2. How it works: 
3. Problems faced and design decisions:

# Part 3
1. Problem Formulation:
  a. State space: All possible groupings of students
  b. Successor function: Add person to group based on preferences or replace based on not wanting to work with someone
  c. Edge weights: Cost of the groupings based on number of complaint emails
  d. Heuristic function: None
2. How it works:
3. Problems faced and design decisions:
