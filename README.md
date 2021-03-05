# Part 1
### 1. Problem Formulation:
   ##### a. State space: 
             4x5 board with 20 tiles numbered 1-20
   ##### b. Successor function: 
             Any legal move of a row or columns (1st, 3rd, and 5th column slide up, 2nd and 4th columns slide down, 1st and 3rd rows slide left, and 2nd and 4th rows slide
             right)
   ##### c. Edge weights: 
             Each move of a tile has a cost of 1.
   ##### d. Heuristic function: 
             The heuristic being used to assign a priority to the successors in the priority queue, is the maximum of the minimum moves required for a tile to reach its goal
             state. The states with the lowest h(s) are given highest priority.
### 2. How it works:
      
### 3. Problems faced and design decisions:
      

# Part 2
### 1. Problem Formulation:
  ##### a. State space: 
            Map of cities and highways
  ##### b. Successor function: 
            Path connecting current location to next location
  ##### c. Edge weights: 
            The weights depends on the user's choice of cost function of either number of road segments, total distance, fastest route, or safest route. 
  ##### d. Heuristic function: 
            If two successor states have the same cost, then a heuristic is used to determine which successor has a smaller distance to the goal city based on the difference
            between latitude and longitude. The successor with the smaller distance is the one chosen by the agent. 
### 2. How it works:
            The program begins by placing the first state in the priority queue into the fringe. The program checks if the current state is the goal city. If it is, then the
            goal state is translated into route taken, total miles, total hours, and total accidents. If it is not the goal state, then each path (city) in the current state
            is checked to see if it has already been visited by the agent. If it has been visited before, then the program moves to the next path in the state. If the path has
            not been visited previously, then it is added to the fringe as the cost function defined by the user. It is also added to the visited cities list to prevent
            returning to the same location. The process continues until the goal city is found by the agent. 
### 3. Problems faced and design decisions:

# Part 3
### 1. Problem Formulation:
Find the groups of students which results in least complaints. On initial analysis, total number of groups of size less 
than or equal to 3 from given 'n' students were calculated using python program.
Following were the results.
1 -> 1 |
2 -> 2 |
3 -> 5 |
4 -> 14 |
5 -> 46 |
6 -> 166 |
7 -> 652 |
8 -> 2780 |
9 -> 12644 |
10 -> 61136 |
11 -> 312676 |

Total number of results increase factorially. So for large set of students, it will be exhaustive to search through all 
possible combinations. 

We have formulated the problem in following way:
1) there is a basic initial state, which is used to generate next possible states. For our case this state is a set of 
   groups where each individual person is present and no other person is part of group.
2) To generate next successor states, every two groups are merged. The merge happens in such a way that the size doesnt 
   exceed "three".
3) For each of these next states, the cost(#complain) is calculated and inserted into the fringe. which acts as a priority.
4) While searching through the states, if a state is reached, which has minimum #complaints, then it is yielded.


  ##### a. State space: 
            All possible groupings of students. We have calculated total number of groups possible with 'n' students and
            it shows factorial growth in the number of distinct groups possible. Here are the results for first 11 numbers.
            1 -> 1 
            2 -> 2 
            3 -> 5 
            4 -> 14 
            5 -> 46 
            6 -> 166 
            7 -> 652 
            8 -> 2780 
            9 -> 12644 
            10 -> 61136 
            11 -> 312676
  ##### b. Initial state:
            In the initial state, each group has only one person, that is the person himself. So in the beginning there
            are n groups, if there are n students.
  ##### c. Successor function: 
            Following requirements were expected of the successor function.
            * We should be able to generate all possible states, that are possible.
            * A state should not be generated again and again. That is we should make sure that same state is not being 
            generated again and again, this will make our seach faster. As the state space is already very exhaustive.

            
            
  ##### d. Edge weights: 
            Cost of the groupings based on number of complaint emails
  ##### e. Heuristic function: 
            None
### 2. How it works:
### 3. Problems faced and design decisions:
