#!/usr/local/bin/python3
# route.py : Find routes through maps
#
# Code by: radverma
#
# Based on skeleton code by V. Mathur and D. Crandall, January 2021
#


# !/usr/bin/env python3
import sys
from queue import PriorityQueue

CITIES = {}

GOAL_CITY = ""
MAX_SEGMENT_LENGTH = 0
MAX_SPEED_HIGHWAY = 0
ENABLE_HEURISTIC = False # if set to false, then h(s) = 0, which is also consistent.

class Segment:
    def __init__(self, dest, length, speed, name):
        self.dest = dest
        self.city = dest.split(",")[0]
        self.state = dest.split(",")[1]
        self.length = float(length)
        self.speed = float(speed)
        self.name = name.strip()

class City:
    def __init__(self, city, lat, lng):
        self.place = city
        self.city = city.split(",")[0] # Stores only the city
        self.state = city.split(",")[1] # Stores only the state
        self.lat = None if not lat else float(lat)
        self.lng = None if not lat else float(lng)
        self.paths = []

    def add_road(self, segment: Segment):
        self.paths.append(segment)

# Code start: Taken from https://janakiev.com/blog/gps-points-distance-python/ Shared by Hongxuan Zhai on QA community.
from math import sin, cos, sqrt, atan2, radians
import math
def distance_lat_lng(lat_lng1, lat_lng2):

    R = 3958.8
    lat1, lon1 = lat_lng1
    lat2, lon2 = lat_lng2

    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)

    a = math.sin(dphi / 2) ** 2 + \
        math.cos(phi1) * math.cos(phi2) * math.sin(dlambda / 2) ** 2

    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))
# Code end: Taken from https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude

class PriorityElem:
    def __init__(self, current_state):
        self.current_state = current_state

    def __lt__(self, other):
        if not ENABLE_HEURISTIC:
            return self.current_state[0] < other.current_state[0]
        return self.current_state[0] + self.current_state[1] < other.current_state[0] + other.current_state[1]

def read_cities():
    global CITIES
    nodes = {}
    with open("city-gps.txt") as file:
        for line in file:
            if not line:
                continue
            attribs = line.split(" ")
            nodes[attribs[0]] = City(*attribs)
    CITIES = nodes

def read_roads():
    global CITIES, MAX_SEGMENT_LENGTH, MAX_SPEED_HIGHWAY
    with open("road-segments.txt") as file:
        for line in file:
            if not line:
                continue
            attribs = line.split(" ")
            if attribs[0] not in CITIES:
                CITIES[attribs[0]] = City(attribs[0], "", "")
            if attribs[1] not in CITIES:
                CITIES[attribs[1]] = City(attribs[1], "", "")
            CITIES[attribs[0]].add_road(Segment(*attribs[1:]))
            CITIES[attribs[1]].add_road(Segment(*(attribs[:1] + attribs[2:])))
            if float(attribs[2]) > MAX_SEGMENT_LENGTH:
                MAX_SEGMENT_LENGTH = float(attribs[2])
            if float(attribs[3]) > MAX_SPEED_HIGHWAY:
                MAX_SPEED_HIGHWAY = float(attribs[3])

def get_accident_on_road_segment(segment: Segment):
    if segment.name[:2] == "I-":
        return segment.length / 1000000
    return segment.length * 2 / 1000000

# This function generates the output from the path segments that have been found.
def get_path_segments(segments):
    route_taken = []
    total_miles = 0
    total_hours = 0
    total_accidents = 0
    for segment in segments:
        route_taken.append((segment.dest, segment.name + " for " + str(segment.length) + " miles"))
        total_miles += segment.length
        total_hours += segment.length / segment.speed
        total_accidents += get_accident_on_road_segment(segment)

    return {"total-segments": len(route_taken),
            "total-miles": total_miles,
            "total-hours": total_hours,
            "total-expected-accidents": total_accidents,
            "route-taken": route_taken}

def get_path_for_segment_state(state):
    return get_path_segments(state[3])

def route_successor(city):
    return CITIES[city].paths

def get_distance_in_cities(city1, city2):
    return distance_lat_lng((CITIES[city1].lat, CITIES[city1].lng), (CITIES[city2].lat, CITIES[city2].lng))

def get_distance_from_goal(city):
    if not ENABLE_HEURISTIC:
        return 0
    if city == GOAL_CITY:
        return 0
    if CITIES[city].lat is not None or CITIES[city].lng is not None:
        return distance_lat_lng((CITIES[city].lat, CITIES[city].lng), (CITIES[GOAL_CITY].lat, CITIES[GOAL_CITY].lng))
    else:
        min_goal_distance = 1000000000
        for segment in CITIES[city].paths:
            if CITIES[segment.dest].lat is None or CITIES[segment.dest].lng is None:
                continue
            consistency_distance = get_distance_from_goal(segment.dest) - segment.length
            if consistency_distance < min_goal_distance:
                min_goal_distance = consistency_distance
        return min_goal_distance

def h_segment(city):
    goal_distance = get_distance_from_goal(city)
    return goal_distance / MAX_SEGMENT_LENGTH

def h_time(city):
    goal_distance = get_distance_from_goal(city)
    return goal_distance / MAX_SPEED_HIGHWAY

def h_safe(city):
    goal_distance = get_distance_from_goal(city)
    return goal_distance/1000000

# Calculates the lat lng distance and tries to estimate the cost.
def h_s(city, type):
    if not ENABLE_HEURISTIC:
        return 0
    if type == "segments":
        return h_segment(city)
    if type == "distance":
        return get_distance_from_goal(city)
    if type == "time":
        return h_time(city)
    if type == "safe":
        return h_safe(city)

def insert_in_fringe(fringe, segment, previous_elem: PriorityElem, type, fringe_cities):
    f_s = previous_elem.current_state[0]
    path = previous_elem.current_state[3] + [segment]
    heuristic_val = h_s(segment.dest, type)
    edge_weight = 0
    if type == "segments":
        edge_weight = 1
    if type == "distance":
        edge_weight = segment.length
    if type == "time":
        edge_weight = segment.length/segment.speed
    if type == "safe":
        edge_weight = get_accident_on_road_segment(segment)

    if segment.dest in fringe_cities and fringe_cities[segment.dest] < (f_s + edge_weight + heuristic_val):
        return
    fringe.put(PriorityElem((f_s + edge_weight, heuristic_val, segment.dest, path)))
    fringe_cities[segment.dest] = f_s + edge_weight + heuristic_val

    # INCONSISTENCY DETECTION CODE.
    # if (previous_elem.current_state[1] - edge_weight) > heuristic_val:
    #     print("Consistency check failed for: " + previous_elem.current_state[2] + " for segment: " + segment.dest + " path name: " + segment.name)
    #     print("previous h(s): " + str(previous_elem.current_state[1]) + " edge weight: " + str(edge_weight) + " current h: " + str(heuristic_val))
    #     print(get_distance_from_goal(previous_elem.current_state[2]))
    #     print(get_distance_from_goal(segment.dest))
    return (f_s + edge_weight, heuristic_val)

def get_route(start, end, cost):

    """
    Find shortest driving route between start city and end city
    based on a cost function.

    1. Your function should return a dictionary having the following keys:
        -"route-taken" : a list of pairs of the form (next-stop, segment-info), where
           next-stop is a string giving the next stop in the route, and segment-info is a free-form
           string containing information about the segment that will be displayed to the user.
           (segment-info is not inspected by the automatic testing program).
        -"total-segments": an integer indicating number of segments in the route-taken
        -"total-miles": a float indicating total number of miles in the route-taken
        -"total-hours": a float indicating total amount of time in the route-taken
        -"total-expected-accidents": a float indicating the expected accident count on the route taken
    2. Do not add any extra parameters to the get_route() function, or it will break our grading and testing code.
    3. Please do not use any global variables, as it may cause the testing code to fail.
    4. You can assume that all test cases will be solvable.
    5. The current code just returns a dummy solution.
    """
    read_cities()
    read_roads()

    global GOAL_CITY
    GOAL_CITY = end

    fringe = PriorityQueue()
    fringe.put(PriorityElem((0, h_s(start, cost), start, [])))

    closed_cities = set()
    cities_in_fringe = {}

    while not fringe.empty():
        elem = fringe.get()
        closed_cities.add(elem.current_state[2])
        if elem.current_state[2] in cities_in_fringe:
            del cities_in_fringe[elem.current_state[2]]

        if elem.current_state[2] == end:
            return get_path_for_segment_state(elem.current_state)
        prev_hs = elem.current_state[1]
        for segment in route_successor(elem.current_state[2]):
            if segment.dest in closed_cities:
                continue
            insert_in_fringe(fringe, segment, elem, cost, cities_in_fringe)

    return get_path_segments([])

# Please don't modify anything below this line
#
if __name__ == "__main__":
    if len(sys.argv) != 4:
        raise(Exception("Error: expected 3 arguments"))

    (_, start_city, end_city, cost_function) = sys.argv
    if cost_function not in ("segments", "distance", "time", "safe"):
        raise(Exception("Error: invalid cost function"))

    result = get_route(start_city, end_city, cost_function)

    # Pretty print the route
    print("Start in %s" % start_city)
    for step in result["route-taken"]:
        print("   Then go to %s via %s" % step)

    print("\n Total segments: %6d" % result["total-segments"])
    print("    Total miles: %10.3f" % result["total-miles"])
    print("    Total hours: %10.3f" % result["total-hours"])
    print("Total accidents: %15.8f" % result["total-expected-accidents"])
