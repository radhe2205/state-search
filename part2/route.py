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
ENABLE_HEURISTIC = False

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

# Code start: Taken from https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude
from math import sin, cos, sqrt, atan2, radians
def distance_lat_lng(lat_lng1, lat_lng2):

    R = 6373.0
    lat1 = radians(lat_lng1[0])
    lon1 = radians(lat_lng1[1])
    lat2 = radians(lat_lng2[0])
    lon2 = radians(lat_lng2[1])

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    return R * c * 0.621371
# Code end: Taken from https://stackoverflow.com/questions/19412462/getting-distance-between-two-points-based-on-latitude-longitude

class PriorityElem:
    def __init__(self, current_state):
        self.current_state = current_state

    def __lt__(self, other):
        if not ENABLE_HEURISTIC:
            if self.current_state[0] == other.current_state[0] \
                    and CITIES[self.current_state[2]].lat is not None \
                    and CITIES[other.current_state[2]].lat is not None:
                return get_distance_from_goal(self.current_state[2]) < get_distance_from_goal(other.current_state[2])

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

def successor_segment(city):
    return CITIES[city].paths

def get_distance_from_goal(city):
    if not ENABLE_HEURISTIC:
        return 0
    if city == GOAL_CITY:
        return 0
    if CITIES[city].lat is not None and CITIES[city].lng is not None:
        return distance_lat_lng((CITIES[city].lat, CITIES[city].lng), (CITIES[GOAL_CITY].lat, CITIES[GOAL_CITY].lng))
    else:
        max_goal_distance = 0
        for segment in CITIES[city].paths:
            if CITIES[segment.dest].lat is None or CITIES[segment.dest].lng is None:
                continue
            consistency_distance = get_distance_from_goal(segment.dest) - segment.length
            if consistency_distance > max_goal_distance:
                max_goal_distance = consistency_distance
        return max_goal_distance

def h_segment(city):
    goal_distance = get_distance_from_goal(city)
    return goal_distance / MAX_SEGMENT_LENGTH

def h_time(city):
    goal_distance = get_distance_from_goal(city)
    return goal_distance / MAX_SPEED_HIGHWAY

def h_safe(city):
    goal_distance = get_distance_from_goal(city)
    return goal_distance/1000000

def h_s(city, type):
    if type == "segments":
        return h_segment(city)
    if type == "distance":
        return get_distance_from_goal(city)
    if type == "time":
        return h_time(city)
    if type == "safe":
        return h_safe(city)

def insert_in_fringe(fringe, segment, previous_elem: PriorityElem, type):
    f_s = previous_elem.current_state[0]
    path = previous_elem.current_state[3] + [segment]

    if type == "segments":
        fringe.put(PriorityElem((f_s + 1, h_s(segment.dest, type), segment.dest, path)))
    if type == "distance":
        fringe.put(PriorityElem((f_s + segment.length, h_s(segment.dest, type), segment.dest, path)))
    if type == "time":
        fringe.put(PriorityElem((f_s + segment.length/segment.speed, h_s(segment.dest, type), segment.dest, path)))
    if type == "safe":
        fringe.put(PriorityElem((f_s + get_accident_on_road_segment(segment), h_s(segment.dest, type), segment.dest, path)))

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

    visited_cities = [start]

    while not fringe.empty():
        elem = fringe.get()
        if elem.current_state[2] == end:
            return get_path_for_segment_state(elem.current_state)
        for segment in successor_segment(elem.current_state[2]):
            if segment.dest in visited_cities:
                continue
            insert_in_fringe(fringe, segment, elem, cost)
            visited_cities.append(segment.dest)

    return get_path_segments([])

    # route_taken = [("Martinsville,_Indiana","IN_37 for 19 miles"), # 52
    #                ("Jct_I-465_&_IN_37_S,_Indiana","IN_37 for 25 miles"), #52
    #                ("Indianapolis,_Indiana","IN_37 for 7 miles")] #30
    #
    # return {"total-segments" : len(route_taken),
    #         "total-miles" : 51,
    #         "total-hours" : 1.07949,
    #         "total-expected-accidents" : 0.000051,
    #         "route-taken" : route_taken}


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
