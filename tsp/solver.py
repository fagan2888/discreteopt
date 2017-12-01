#!/usr/bin/python
# -*- coding: utf-8 -*-

import math
import time
import random
import pdb
from datetime import datetime
from collections import namedtuple

Point = namedtuple("Point", ['x', 'y'])

global POINTS

def length(point1, point2):
    return math.sqrt((point1.x - point2.x)**2 + (point1.y - point2.y)**2)

def solve_it(input_data):
    global POINTS

    # Modify this code to run your optimization algorithm
    random.seed(1847859218408232171737)
    # parse the input
    lines = input_data.split('\n')

    nodeCount = int(lines[0])

    points = []
    for i in range(1, nodeCount+1):
        line = lines[i]
        parts = line.split()
        points.append(Point(float(parts[0]), float(parts[1])))

    POINTS = points
    print('Problem instance with N = {}'.format(len(POINTS)))
    print('Starts at {}'.format(datetime.now().time()))
    # build a trivial solution
    # visit the nodes in the order they appear in the file
    #solution = range(0, nodeCount)

    #guess = [x for x in range(0, nodeCount)]
    #random.shuffle(guess)
    guess = make_initial_guess(nodeCount)
    print(guess)
    solution = local_search(POINTS, guess, state_value(guess))

    # calculate the length of the tour
    obj = state_value(solution)

    # prepare the solution in the specified output format
    output_data = '%.2f' % obj + ' ' + str(0) + '\n'
    output_data += ' '.join(map(str, solution))

    return output_data

def make_initial_guess(node_count):
    global POINTS
    s = set(range(node_count))
    guess = [s.pop()]
    while len(s) > 1:
        min_dist = -1
        best = None
        for elem in s:
            if min_dist == -1 or\
               length(POINTS[guess[-1]], POINTS[elem]) < min_dist:
                min_dist = length(POINTS[guess[-1]], POINTS[elem])
                best = elem
        guess.append(best)
        s.remove(best)
    guess.append(s.pop())
    return guess

def state_value(solution):
    global POINTS
    obj = length(POINTS[solution[-1]], POINTS[solution[0]])
    for index in range(0, len(POINTS)-1):
        obj += length(POINTS[solution[index]], POINTS[solution[index+1]])
    return obj

def _accept(current, novel, temperature):
    old_val = state_value(current)
    new_val = state_value(novel)
    if new_val <= old_val: return True
    #if random.random() > 0.5: return True
    #threshold = 0.5
    #if math.exp((new_val - old_val) / temperature) > random.random():
    #    return True
    return False

def local_search(points, guess, guess_val):
    T0 = round(guess_val/2) # initial temperature
    time_limit = 300 # seconds
    tabu = [] # keep last 1k visited states
    tabu_size = 5000
    start = time.time()
    best = guess.copy()
    current = guess
    tabu.append(current)
    T = T0
    maxStep = 1e6
    max_tries = 0
    empty_neigh = 0
    delta = T0 / maxStep
    for i in range(int(maxStep)-1):
        neigh = find_neigh(current, tabu)
        if neigh is not None:
            empty_neigh = 0
            tabu.append(neigh)
            if len(tabu) == tabu_size + 1:
                tabu = tabu[1:]
            if _accept(current, neigh, T) or\
                max_tries == 200:
                max_tries = 0
                current = neigh
                if state_value(current) < state_value(best):
                    best = current.copy()
            else:
                max_tries += 1
        else:
            empty_neigh += 1
        if empty_neigh == 500:
            empty_neigh = 0
            random.shuffle(current)
        diff = time.time() - start
        #print('Diff is {}'.format(diff))
        if diff > time_limit:
            print("Time interruption at step {}".format(i))
            break
        T -= delta
    assert(assert_sol(best, len(points)))
    return best

def find_neigh(current, tabu):
    global POINTS
    all_sol = k_opt(current)
    all_sol.sort(key=lambda x: state_value(x))
    for s in all_sol:
        if not is_permutation(current, s):
            if not s in tabu:
                return s
    return None

def is_permutation(sol1, sol2):
    j1 = 0
    j2 = sol2.index(sol1[j1])
    while j1 < len(sol1):
        if sol1[j1] != sol2[j2 % len(sol2)]:
            return False
        j1 += 1
        j2 += 1
    return True

def k_opt(curr_sol):
    global POINTS
    all_sol = []
    rand = random.randint(0, len(curr_sol)-1)
    x1 = (curr_sol[rand-1], rand-1)
    x2 = (curr_sol[rand], rand)
    opt = 5
    current = curr_sol
    while opt > 0:
        length1 = length(POINTS[x1[0]], POINTS[x2[0]])
        x3 = None
        to_avoid = {x1[1], x1[1] % len(POINTS),
                    x2[1], x2[1] % len(POINTS),
                    x2[1]+1, (x2[1]+1) % len(POINTS)}
        for i in range(len(current)):
            if i not in to_avoid and\
                length(POINTS[x2[0]], POINTS[i]) < length1:
                x3 = (current[i], i)
                break
        if x3 is None:
            return all_sol
        x4 = (current[x3[1]-1], x3[1]-1)
        a_sol = [x2[0], x3[0]]
        i = x3[1] + 1
        while current[i % len(POINTS)] != x1[0]:
            a_sol.append(current[i % len(POINTS)])
            i += 1
        a_sol += [x1[0], x4[0]]
        i = x4[1] - 1
        while current[i % len(POINTS)] != x2[0]:
            a_sol.append(current[i % len(POINTS)])
            i -= 1
        if len(set(a_sol)) != len(POINTS):
            raise ValueError('Stmg is wrong')
        all_sol.append(a_sol.copy())
        opt -= 1
        x1 = (x1[0], a_sol.index(x1[0]))
        x2 = (x4[0], a_sol.index(x4[0]))
        current = a_sol.copy()
    return all_sol
    

def assert_sol(solution, tot):
    return len(set(solution)) == tot


import sys

if __name__ == '__main__':
    import sys
    if len(sys.argv) > 1:
        file_location = sys.argv[1].strip()
        with open(file_location, 'r') as input_data_file:
            input_data = input_data_file.read()
        print(solve_it(input_data))
    else:
        print('This test requires an input file.  Please select one from the data directory. (i.e. python solver.py ./data/tsp_51_1)')

