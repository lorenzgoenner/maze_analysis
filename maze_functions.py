from pylab import *

def calc_agent_direction(rooms, doors, room_index, door_index):
    # Input:  Room index where the agent is currently located
    # Output: Direction the agent is facing towards (0,1,2,3 <-> N,E,S,W)
    x_ag, y_ag = rooms['x'][room_index], rooms['y'][room_index]
    x_door, y_door = doors['position_x'][door_index], doors['position_y'][door_index]
    agent_direction_NESW = ''
    if x_door == x_ag:
        if y_door > y_ag:
            agent_direction_NESW = 2 # 'south'
        elif y_door < y_ag:
            agent_direction_NESW = 0 # 'north'
    elif y_door == y_ag:
        if x_door > x_ag:
            agent_direction_NESW = 3 # 'west'
        elif x_door < x_ag:
            agent_direction_NESW = 1 # 'east'
    return agent_direction_NESW


def calc_door_direction(doors, door_index):
    # Input: Door index (0 .. 23)
    # Output: Door direction (0,1,2,3 <-> N,E,S,W)
    door_ind = int(door_index)
    door_direction_NESW = nan # ''
    if doors['diff_x'][door_ind] == 0:
        if (doors['diff_y'][door_ind] > 0 and doors['direction'][door_ind] == 1) or (doors['diff_y'][door_ind] < 0 and doors['direction'][door_ind] == -1):
            door_direction_NESW = 0 # 'north'
        elif (doors['diff_y'][door_ind] < 0 and doors['direction'][door_ind] == 1) or (doors['diff_y'][door_ind] > 0 and doors['direction'][door_ind] == -1):
            door_direction_NESW = 2 # 'south'
    elif doors['diff_y'][door_ind] == 0:
        if (doors['diff_x'][door_ind] > 0 and doors['direction'][door_ind] == 1) or (doors['diff_x'][door_ind] < 0 and doors['direction'][door_ind] == -1):
            door_direction_NESW = 1 # 'east'
        elif (doors['diff_x'][door_ind] < 0 and doors['direction'][door_ind] == 1) or (doors['diff_x'][door_ind] > 0 and doors['direction'][door_ind] == -1):
            door_direction_NESW = 3 # 'west'
    return door_direction_NESW


def calc_door_position_NESW(rooms, doors, door_index_array, curr_room):
    # Input: Door index (0 .. 23)
    # Output: Door position relative to the center of the current room (0,1,2,3 <-> N,E,S,W)
    n_doors = len(door_index_array)
    door_position_NESW = nan * ones(n_doors)
    for i_door in xrange(n_doors):
		if isnan(door_index_array[i_door])==False:
			door_ind = int(door_index_array[i_door])
			Dx_door_room = doors['position_x'][door_ind] - rooms['x'][int(curr_room)]
			Dy_door_room = doors['position_y'][door_ind] - rooms['y'][int(curr_room)]
			if Dx_door_room == 0:
				if Dy_door_room > 0:
				    door_position_NESW[i_door] = 0 # 'north'
				elif Dy_door_room < 0:
				    door_position_NESW[i_door] = 2 # 'south'
			elif Dy_door_room == 0:
				if Dx_door_room > 0:
				    door_position_NESW[i_door] = 1 # 'east'
				elif Dx_door_room < 0:
				    door_position_NESW[i_door] = 3 # 'west'
    return door_position_NESW


def check_door_flip(flipdata, doors):
    # Input:  Array of binary values ("1" indicates a flipped door after the current trial)
    # Output: Updated "doors" dictionary
    flipdata_int = zeros(len(flipdata))
    for i in xrange(len(flipdata)):
        flipdata_int[i] = int(flipdata[i])
    nz_flip = nonzero(flipdata_int)[0]
    for i_flipped in xrange(len(nz_flip)):
        doors['direction'][nz_flip[i_flipped]] *= -1
    return doors


def coord_transform(response_key, curr_dir):
     # Input: response 1 = 'left', response 2 = 'ahead', response 3 = 'right'
     # Output: N,E,S,W <=> 0,1,2,3
     # Default output value is 'nan' (used to indicate 'trivial' choices with only one door)
    chosen_dir = nan
    if int(response_key) == 1:
        chosen_dir = mod(curr_dir - 1, 4)
    elif int(response_key) == 2:
        chosen_dir = curr_dir
    elif int(response_key) == 3:
        chosen_dir = mod(curr_dir + 1, 4)
    #else: print "Error: Response key out of range, should be 1,2 or 3"
    return chosen_dir


def calc_room_successor_value(choices, doors, room_at_dec, avail_doors, state_value_const, i_trial):
	# Used for fitting the successor representation    
	# Input:  state_value_const: 16 values (one per room)
	# Output: room_successors_currtrial (up to four rooms)
	#         room_successor_value_currtrial (up to four values)
	#         choice_options_NESW_currtrial (up to four values)
	choice_options_NESW_currtrial = nan * ones(4)
	room_successors_currtrial = nan * ones(4)
	room_successor_value_currtrial = nan * ones(4)
	open_doors_index = nan * ones(4)
	for j_door in xrange(len(avail_doors)):
		nz_curr_room = nonzero(doors['connects'][int(avail_doors[j_door])] == int(room_at_dec[i_trial]))[0]
		if nz_curr_room==0 and doors['direction'][int(avail_doors[j_door])] == 1 or nz_curr_room==1 and doors['direction'][int(avail_doors[j_door])] == -1:
		    # Get the available actions (N,E,S,W <-> 0,1,2,3) corresponding to the available doors:
		    choice_options_NESW_currtrial[j_door] = calc_door_direction(doors, avail_doors[j_door])
		    # Get the room indices
		    if nz_curr_room==0 and doors['direction'][int(avail_doors[j_door])] == 1:
		        room_succ_index = int(doors['connects'][int(avail_doors[j_door])][1])
		        room_successors_currtrial[j_door] = room_succ_index
		        room_successor_value_currtrial[j_door] = state_value_const[room_succ_index]
		        open_doors_index[j_door] = avail_doors[j_door]
		    elif nz_curr_room==1 and doors['direction'][int(avail_doors[j_door])] == -1:
		        room_succ_index = int(doors['connects'][int(avail_doors[j_door])][0])
		        room_successors_currtrial[j_door] = room_succ_index
		        room_successor_value_currtrial[ j_door] = state_value_const[room_succ_index]
		        open_doors_index[j_door] = avail_doors[j_door]
	return room_successors_currtrial, room_successor_value_currtrial, choice_options_NESW_currtrial, open_doors_index



def calc_room_successor_value_doors(choices, doors, room_at_dec, avail_doors, state_action_values, i_trial):
	# Used for fitting Q-learning
	# Input:  state_action_values: 24 values (one per door)
	# Output: room_successors_currtrial (up to four rooms)
	#         state_action_values_currtrial (up to four values)
	#         choice_options_NESW_currtrial (up to four values)

	state_action_values_currtrial = nan * ones(4)

	open_doors_index = calc_opendoors(doors, room_at_dec, avail_doors, i_trial)
	#print "avail_doors = ", avail_doors
	#print "open_doors_index = ", open_doors_index

	for j_door in xrange(len(open_doors_index)):
		if isnan(open_doors_index[j_door])==False:
		    state_action_values_currtrial[j_door] = state_action_values[int(open_doors_index[j_door])]
		    #print "state_action_values_currtrial[j_door] = ", state_action_values_currtrial[j_door]

	return state_action_values_currtrial,  open_doors_index



def calc_opendoors(doors, room_at_dec, avail_doors, i_trial):
	# Used by Q-learning & planning
	# Output: Index of all doors which are accessible in the current trial  
	open_doors_index = nan * ones(4)
	for j_door in xrange(len(avail_doors)):
		nz_curr_room = nonzero(doors['connects'][int(avail_doors[j_door])] == int(room_at_dec[i_trial]))[0]
		if nz_curr_room==0 and doors['direction'][int(avail_doors[j_door])] == 1 or nz_curr_room==1 and doors['direction'][int(avail_doors[j_door])] == -1:
		    # Get the available actions (N,E,S,W <-> 0,1,2,3) corresponding to the available doors:
		    # Get the room indices
		    if nz_curr_room==0 and doors['direction'][int(avail_doors[j_door])] == 1:
		        open_doors_index[j_door] = int(avail_doors[j_door])
		    elif nz_curr_room==1 and doors['direction'][int(avail_doors[j_door])] == -1:
		        open_doors_index[j_door] = int(avail_doors[j_door])
	return open_doors_index


def read_door_options_NESW(str_line, room_curr, col):
    # Input: A string array (one line of the log file)
    #        Entries "0" or "1" in columns 14-17 indicate whether each door is currently open (1) or closed (0)
    # Output: Integer array containing the same information
    open_doors = nan * ones(4)
    if int(str_line[col['exitN']]) == 1:
        open_doors[0] = 0
    if int(str_line[col['exitE']]) == 1:
        open_doors[1] = 1
    if int(str_line[col['exitS']]) == 1:
        open_doors[2] = 2
    if int(str_line[col['exitW']]) == 1:
        open_doors[3] = 3
    return open_doors



def update_doors_with_log(doors, excess_door_ind, missing_door_ind):
    for i_excess in excess_door_ind:
        doors['direction'][int(i_excess)] *= -1
    for i_missing in missing_door_ind:
        doors['direction'][int(i_missing)] *= -1
    return doors



def calc_room_successor(doors, current_room, avail_doors):
	# Output: room_successors_currtrial
	room_successors_currtrial = nan * ones(4)
	for j_door in xrange(len(avail_doors)):
		if isnan(avail_doors[j_door])== False:
		    nz_curr_room = nonzero(doors['connects'][int(avail_doors[j_door])] == int(current_room))[0]
		    if nz_curr_room==0 and doors['direction'][int(avail_doors[j_door])] == 1 or nz_curr_room==1 and doors['direction'][int(avail_doors[j_door])] == -1:
		        # Get the room indices
		        if nz_curr_room==0 and doors['direction'][int(avail_doors[j_door])] == 1:
		            room_succ_index = int(doors['connects'][int(avail_doors[j_door])][1])
		            room_successors_currtrial[j_door] = room_succ_index
		        elif nz_curr_room==1 and doors['direction'][int(avail_doors[j_door])] == -1:
		            room_succ_index = int(doors['connects'][int(avail_doors[j_door])][0])
		            room_successors_currtrial[j_door] = room_succ_index
	return room_successors_currtrial

def calc_choice_options_NESW(doors, avail_doors, room_at_dec, i_trial):
	choice_options_NESW_currtrial = nan * ones(4)
	for j_door in xrange(len(avail_doors)):
		nz_curr_room = nonzero(doors['connects'][int(avail_doors[j_door])] == int(room_at_dec[i_trial]))[0]
		if nz_curr_room==0 and doors['direction'][int(avail_doors[j_door])] == 1 or nz_curr_room==1 and doors['direction'][int(avail_doors[j_door])] == -1:
		    # Get the available actions (N,E,S,W <-> 0,1,2,3) corresponding to the available doors:
		    choice_options_NESW_currtrial[j_door] = calc_door_direction(doors, avail_doors[j_door])
	return choice_options_NESW_currtrial




