from pylab import *

from init_door_config import rooms, transitions, doors, neighbours, n_rooms, n_doors, calc_transitions# , draw_doors, place_reward, draw_reward, 
from maze_functions import calc_room_successor # calc_room_successor_value #  calc_agent_direction, calc_door_direction, calc_door_position_NESW, check_door_flip, coord_transform,

def calc_Q_plan(current_room, open_doors, prev_door, P_belief, gamma, eta):
    # TODO: Complete & correct!
    Q_plan_rooms = zeros([n_rooms, 4])
    n_reps = 16 # 1 # 16
    for i_reps in xrange(n_reps):
        # 1. Get available doors & update beliefs
        # 2. Check if any of the available doors leads to a reward site
        # 3. For the doors that don't, update Q_plan by Eq. (7) & (8) in Simon & Daw (2011)
        #    (Strategy: Calc. the probability)

        P_belief = update_belief(P_belief, current_room, open_doors, eta)
        room_successors = calc_room_successor(doors, current_room, open_doors) # all_room_doors = rooms['door_list'][curr_room, :]

        #print "room_successors = ", room_successors
        #print "open_doors = ", open_doors

        bf_list = bfs(rooms['neighbour'], current_room)
        #print "bf_list = ", bf_list
        for i_room in bf_list:
            # Get available doors & corresponding room successors
            room_doors = rooms['door_list'][int(i_room), :]
            #room_successors = rooms['neighbour'][i_room, :] # calc_room_successor(doors, i_room, room_doors) # ALL neighbours
            room_successors = get_neighbours_from_doors(i_room, room_doors, doors)
            #print "room_doors = ", room_doors
            #print "room_successors = ", room_successors

            for i_door in xrange(len(room_doors)): # During planning, use all doors regardless of their state - currently closed doors have zero prob. of being open
                door_ind4 = nonzero(room_doors[i_door] == rooms['door_list'][int(i_room), :])[0]
                if isnan(room_doors[i_door]) == False:
                    if rooms['reward'][ int(room_successors[i_door]) ] > 0:
                        Q_plan_rooms[int(i_room), door_ind4] = rooms['reward'][ int(room_successors[i_door]) ]
                         #print "rooms['reward'][ int(room_successors[i_door]) ] = ", rooms['reward'][ int(room_successors[i_door]) ]
                    else:
                        Q_plan_rooms[int(i_room), door_ind4] = calculate_Q_plan(Q_plan_rooms, room_doors[i_door], P_belief, doors, int(i_room), prev_door, gamma)


        #print "i_reps, Q_plan_rooms = ", i_reps, Q_plan_rooms
    return Q_plan_rooms


def bfs(graph, initial):
    # Implements a breadth-first search, based on the example provided at www.codespeedy.com/breadth-first-search-algorithm-in-python/
    visited = []
    queue = [initial]
    while queue:
        node = queue.pop(0)
        if node not in visited:
            if isnan(node)==False: 
                visited.append(node)
                neighbours = graph[int(node)]
                for neighbour in neighbours:
                    queue.append(neighbour)
    return visited


def calculate_Q_plan(Q_plan_rooms, curr_door, P_belief, doors, current_room, prev_door, gamma):
    # See Eqs. (7) and (8) in Simon & Daw (2011):
    # Concept:
    # During planning, in room s, we will consider all possible combinations of doors being open or closed.
    # For each of these combinations, we will compute the probability based on the current belief (=at the start of planning).
    # This corresponds to Bernoulli trials (coin tosses) with a different probability for each door.
    # The expectation of "Q-value" with respect to the current belief is then given by the weighted sum of
    # "maximum value of reachable neighboring states", weighted by the probability of the respective combination of open/closed doors.
    # The "no-backtrack" condition has to be applied during the summation over possible sets of doors.
    # The probability of "all doors are closed" is used to compute the conditional probabilitiy of a combination of doors being open,
    # conditional on "at least one door being open".

    # For each set of doors, the probability of these being open or closed corresponds to a Bernoulli trial:
    # P[door_i=open, door_j=open, door_k=open]  =  P[door_i=open] * P[door_j=open] * P[door_k=open]
    # etc. 
    # Now, I have to sum all probabilities of all kinds of combination of open and closed doors:
    # P[door_i=open, door_j=closed] + P[door_i=closed, door_j=open] + ... (etc. - up to 8 combinations.)
    # Without the no-backtrack condition, I would have to sum up to 16 combinations of open and closed doors!

    # What is the structure of P_belief?
    # - For every room, I keep a belief of all doors

    # Here or outside this function:
    # - Get all doors connected to the current room (exclude the backtracking door!)
    # - Iterate over all combinations of open and closed doors
    # - Calculate the probability of each combination of open/closed doors
    # - Compute the probability-weighted sum of value over all combinations, as in Eq. (7)


    all_doors = rooms['door_list'][current_room, :]
    forward_doors = setdiff1d(all_doors, prev_door) # List of doors in the room excluding the "backtrack" door
    forward_doors = forward_doors[isnan(forward_doors)==False]
    n_roomdoors = len(forward_doors)
    forward_rooms = get_neighbours_from_doors(current_room, forward_doors, doors) # "room successors/neighbours" ordered by the list of forward doors

    #print "calculate_Q_plan: current_room = ", current_room
    #print "forward_rooms = ", forward_rooms
    #print "room_successors = ", room_successors

    sum_prob_times_Qsucc = 0.0

    if n_roomdoors==1:
        # If there is only a single "forward" door, the conditional probability of that door being open (conditional on at least one door being open) equals 1!
        i_door0 = nonzero(rooms['door_list'][current_room, :] == forward_doors[0])[0]
        Q_succ_0 = Q_plan_rooms[int(forward_rooms[0]), :].max()
        sum_prob_times_Qsucc = Q_succ_0

    elif n_roomdoors==2: 
        sum_prob_times_Qsucc = 0.0
        i_door0 = nonzero(rooms['door_list'][current_room, :] == forward_doors[0])[0]
        i_door1 = nonzero(rooms['door_list'][current_room, :] == forward_doors[1])[0]
        # Calculate the denominator of Eq. 8:
        prob_allclosed = (1 - P_belief[int(current_room), int(i_door0)]) * (1 - P_belief[int(current_room), int(i_door1)])
        for door_0_state in xrange(2): # 0 = closed, 1 = open
            for door_1_state in xrange(2):
                prob_door0 = door_0_state * P_belief[int(current_room), int(i_door0)] + (1 - door_0_state) * (1 - P_belief[int(current_room), int(i_door0)])
                prob_door1 = door_1_state * P_belief[int(current_room), int(i_door1)] + (1 - door_1_state) * (1 - P_belief[int(current_room), int(i_door1)])
                Q_succ_0 = Q_plan_rooms[int(forward_rooms[0]), :].max()
                Q_succ_1 = Q_plan_rooms[int(forward_rooms[0]), :].max()
                if door_0_state + door_1_state > 0: # Exclude "all doors closed" 
                    prob = prob_door0 * prob_door1 / (1-prob_allclosed)
                    sum_prob_times_Qsucc += prob * max(Q_succ_0, Q_succ_1)

    elif n_roomdoors==3: # TODO: Exclude "all doors closed"
        sum_prob_times_Qsucc = 0.0

        i_door0 = nonzero(rooms['door_list'][current_room, :] == forward_doors[0])[0]
        i_door1 = nonzero(rooms['door_list'][current_room, :] == forward_doors[1])[0]
        i_door2 = nonzero(rooms['door_list'][current_room, :] == forward_doors[2])[0]

        prob_allclosed = (1 - P_belief[int(current_room), int(i_door0)]) * (1 - P_belief[int(current_room), int(i_door1)]) * (1 - P_belief[int(current_room), int(i_door2)])

        for door_0_state in xrange(2):
            for door_1_state in xrange(2):
                for door_2_state in xrange(2):
                    prob_door0 = door_0_state * P_belief[int(current_room), int(i_door0)] + (1 - door_0_state) * (1 - P_belief[int(current_room), int(i_door0)])
                    prob_door1 = door_1_state * P_belief[int(current_room), int(i_door1)] + (1 - door_1_state) * (1 - P_belief[int(current_room), int(i_door1)])
                    prob_door2 = door_2_state * P_belief[int(current_room), int(i_door2)] + (1 - door_2_state) * (1 - P_belief[int(current_room), int(i_door2)])
                    Q_succ_0 = Q_plan_rooms[int(forward_rooms[0]), :].max()
                    Q_succ_1 = Q_plan_rooms[int(forward_rooms[1]), :].max()
                    Q_succ_2 = Q_plan_rooms[int(forward_rooms[2]), :].max()
                    prob = prob_door0 * prob_door1 * prob_door2 / (1-prob_allclosed)
                    sum_prob_times_Qsucc += prob * max(Q_succ_0, Q_succ_1, Q_succ_2)
    #print "sum_prob_times_Qsucc = ", sum_prob_times_Qsucc
    Q_room_door = gamma * sum_prob_times_Qsucc

    return Q_room_door


def init_belief(rooms, n_rooms):
	# Initialize beliefs about door state
	# Structure: Door index is ordered as in rooms['door_list']
	P_belief = nan * ones([n_rooms, 4])
	for i_room in xrange(n_rooms):
	    for i_door in xrange(4):
	        if isnan(rooms['door_list'][i_room, i_door]) == False:
	            P_belief[i_room, i_door] = 0.5
	return P_belief


def update_belief(P_belief, curr_room, open_doors, eta):
	# Decay of beliefs, because doors may have flipped in the meantime:
	for i_room in xrange(n_rooms):
	    P_belief[int(curr_room), :] += eta * (0.5 - P_belief[int(curr_room), :])

	# Update beliefs about open doors based on the observation from the current trial
	all_room_doors = rooms['door_list'][curr_room, :]
	for i_door in all_room_doors: # Iterate through all the doors in the current room regardless of their state
	    door_ind_4 = nonzero(i_door == open_doors)[0]
	    if len(door_ind_4) > 0:
	        P_belief[int(curr_room), door_ind_4] = 1.0 # Door is currently open
	    else:
	        P_belief[int(curr_room), door_ind_4] = 0.0 # Door is closed
	return P_belief


def get_neighbours_from_doors(current_room, forward_doors, doors):
    forward_rooms = nan * ones(len(forward_doors))
    for i_door in xrange(len(forward_doors)):
        if isnan(forward_doors[i_door]) == False:
            nz_succ_room = nonzero(current_room <> doors['connects'][int(forward_doors[i_door])])[0]
            forward_rooms[i_door] = doors['connects'][int(forward_doors[i_door])][nz_succ_room]
    return forward_rooms










