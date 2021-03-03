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

def diff_lat_lng(src, dest):
    if CITIES[src].lat is None or CITIES[src].lng is None or CITIES[dest].lat is None or CITIES[dest].lng is None:
        return 0
    return abs(CITIES[src].lat - CITIES[dest].lat) + abs(CITIES[src].lng - CITIES[dest].lng)

class PriorityElem:
    def __init__(self, current_state):
        self.current_state = current_state

    def __lt__(self, other):
        if self.current_state[0] != other.current_state[0]:
            return self.current_state[0] < other.current_state[0]
        return diff_lat_lng(self.current_state[1], GOAL_CITY) < diff_lat_lng(other.current_state[1], GOAL_CITY)


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
    return get_path_segments(state[2])

def successor_segment(city):
    return CITIES[city].paths

def insert_in_fringe(fringe, segment, previous_elem: PriorityElem, type):
    if type == "segments":
        fringe.put(PriorityElem((previous_elem.current_state[0] + 1, segment.dest, previous_elem.current_state[2] + [segment])))
    if type == "distance":
        fringe.put(PriorityElem((previous_elem.current_state[0] + segment.length, segment.dest, previous_elem.current_state[2] + [segment])))
    if type == "time":
        fringe.put(PriorityElem((previous_elem.current_state[0] + segment.length/segment.speed, segment.dest, previous_elem.current_state[2] + [segment])))
    if type == "safe":
        fringe.put(PriorityElem((previous_elem.current_state[0] + get_accident_on_road_segment(segment), segment.dest, previous_elem.current_state[2] + [segment])))

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
    fringe.put(PriorityElem((0, start, [])))

    visited_cities = [start]

    while not fringe.empty():
        elem = fringe.get()
        if elem.current_state[1] == end:
            return get_path_for_segment_state(elem.current_state)
        for segment in successor_segment(elem.current_state[1]):
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
