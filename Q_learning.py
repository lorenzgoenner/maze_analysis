from pylab import *
from init_door_config import  rooms, transitions, doors, neighbours, n_rooms, n_doors
from maze_functions import calc_door_position_NESW, calc_opendoors

def update_Q_TD(Q_TD, e_traces, TD_params, reward_map, curr_trial, room_at_dec, i_atDoor_curr, jump, choice_NESW, avail_door_list):
    # Note: For "trivial" choices with only one open door,
    # no update should be performed - no accumulation of traces (but decay), no prediction error, no Q-value update

    # TODO: Implement TD updates!

    Q0, alpha, gamma, TD_lambda, beta_inp = TD_params
    # Decay traces for all doors:    
    for i_door in xrange(n_doors):
        e_traces[i_door] *= gamma * TD_lambda


    if isnan(choice_NESW) == False: # Exclude "trivial" choices
        # Retrieve index of the current door:
        open_door_index = calc_opendoors(doors, room_at_dec, avail_door_list, curr_trial)
        open_door_pos_calc_NESW = calc_door_position_NESW(rooms, doors, open_door_index, room_at_dec[curr_trial])
        nz_door_choice = nonzero(open_door_pos_calc_NESW == choice_NESW)[0]
        i_chosen_door = nan
        if len(nz_door_choice) > 0: # and isnan(choice_NESW)==False:
            i_chosen_door = int(open_door_index[nz_door_choice])
        # Update trace of the current door:        
        if isnan(i_chosen_door) == False:            
            e_traces[i_chosen_door] += 1        

    # Truncate traces in case of a jump:            
    for i_door in xrange(n_doors):
        e_traces[i_door] *= (1 - int(jump))
        
    if isnan(choice_NESW) == False:        
        nz_doors = nonzero(isnan(open_door_index) == False)[0]
        if len(nz_doors)==0:
            print "Error (function update_Q_TD) - no doors available ?!"
            return
        Q_TD_opendoors = zeros(len(nz_doors))
        for i_opendoor in xrange(len(nz_doors)):
            Q_TD_opendoors[i_opendoor] = Q_TD[i_opendoor]
        # Value prediction:                    
        v = reward_map[int(room_at_dec[curr_trial])] + gamma * max(Q_TD_opendoors)
        # Prediction error:        
        #delta_RPE = v - Q_TD[int(room_at_dec[curr_trial])] # ERROR - Q_TD should be indexed by a DOOR, not a ROOM!
        delta_RPE = v - Q_TD[int(i_atDoor_curr)]  
        #print "delta_RPE = ", delta_RPE
        # TD update for all doors:  
        for i_door in xrange(n_doors):
            Q_TD[i_door] += alpha * e_traces[i_door] * delta_RPE

    return Q_TD, e_traces
