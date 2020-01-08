from pylab import *
from init_door_config import calc_transitions, draw_doors, place_reward, draw_reward, rooms, transitions, doors, neighbours, n_rooms, n_doors
from trunc_script_lg import plot_path, draw_rooms, plot_transitions
from successor_rep import calc_SR, plot_occupancy

from maze_functions import calc_agent_direction, calc_door_direction, calc_door_position_NESW, check_door_flip, coord_transform, calc_room_successor_value, read_door_options_NESW, update_doors_with_log
from model_fitting import softmax_array, nll, update_nll, calc_lrandom
from log_info import col, line

from time import sleep

import scipy.optimize as sciopt

# Note:
# In the logfile, an entry of "1" in the column labeled "Door_x" means that the corresponding door was flipped after the particpant's decision in that trial
# Similarly, an entry of "1" in the column labeled "Jump" indicates that the agent was teleported after the participant's decision in that trial


# Steps towards fitting a model / obtaining parameter estimates:
# 1. Define action values (respecting the data) as a function of the free parameters
#    - for the simplest fixed successor representation: Table of state values as a function of gamma (discount rate)

# I next want to calculate:
# The best-fitting value of beta (inverse temperature)
# i.e. minimize the negative log-likelihood
# TODO: scipy.optimize.curve_fit() vs. scipy.optimize.minimize()




def check_jump(jump_flag, doors, col):
    # Currently obsolete?!
    col_atDoor = 9
    if int(jump_flag) == 1:
        print "Before jump: doors['direction'][int(col['atDoor'])] = ", doors['direction'][int(col['atDoor'])]
        doors['direction'][int(col['atDoor'])] *= -1
        print "After jump: doors['direction'][int(col['atDoor'])] = ", doors['direction'][int(col['atDoor'])]
    return doors


def read_open_doors(str_line, room_curr, rooms, doors):
    # Currently obsolete?!
    open_doors = nan * ones(4)
    all_doors = rooms['door_list'][room_curr]
    for i in xrange(4):
        if isnan(all_doors[i]) == False:
            open_doors[i] = calc_door_direction(doors, all_doors[i])
    return

def calc_model_fit(params, fixed_params):    
	# Input: fl (Result of file.readlines())
	global doors
	global neighbours

	beta_inp = params[0]
	SR_lambda = params[1]
    
	fl = fixed_params[0]
	i_subj = fixed_params[1]
   
	room_at_decision = nan * ones([500, n_subjects])
	open_door_count = nan * ones([500, n_subjects])
	choice_NESW = nan * ones([500, n_subjects])
	choice_options_NESW = nan * ones([500, 4, n_subjects])
	choice_options_NESW_log = nan * ones([500, 4, n_subjects])
	room_successors = nan * ones([500, 4, n_subjects])
	room_successor_value = nan * ones([500, 4, n_subjects])


	trial_reward = nan * ones(500)
	trial_rewardsum = nan * ones(500)
	trial_steps = nan * ones(500)

	nll_0 = 0
	ptot_0 = 1

	l_random = 0.0


	for i in range(len(fl)): # first data line = line 27
		if len(fl[i].split()) > 18 and i>line['descr']: # Excluding header lines
			# Read from log file
			curr_trial  = int(fl[i].split()[0])-1
			i_room_current = int( fl[i].split()[col['atRoom']] )
			i_atDoor_current = int( fl[i].split()[col['atDoor']] )
			room_at_decision[curr_trial, i_subj] = i_room_current
			door_flip_data = fl[i].split()[col['door0'] : col['door0'] + 23]
			resp_key_LSR = fl[i].split()[col['response_key']] # is one of 1,2,3 (left, straight ahead, right)
			open_door_count[curr_trial, i_subj] = int(fl[i].split()[col['exitN']]) + int(fl[i].split()[col['exitE']]) + int(fl[i].split()[col['exitS']]) + int(fl[i].split()[col['exitW']])
			agent_dir_NESW = calc_agent_direction(rooms, doors, i_room_current, i_atDoor_current)
			if open_door_count[curr_trial, i_subj] > 1:
				choice_NESW[curr_trial, i_subj] = coord_transform(resp_key_LSR, agent_dir_NESW) # Default value is nan for "trivial" choices with only one door

			# Update door state - before or after calculating neighbours and values?!
			doors = check_door_flip(door_flip_data, doors) # Although I compare the door state with the log further below, disabling this makes a difference!
			transitions, neighbours, connections = calc_transitions(doors, neighbours, n_doors) 

			# Strategy 1: (first try)
			# - Find the available doors in the current room
			# - Find the actions (N,E,S,W) corresponding to these doors
			# - Find the rooms to which these actions will lead
			# - Find the value associated to each of these rooms
			curr_neighbours = nonzero(neighbours[ i_room_current, : ])[0]
			# Get indices of those doors connecting the current state to its neighbours:
			avail_door_list = rooms['door_list'][i_room_current]	    
			avail_doors = avail_door_list[isnan(avail_door_list)==False]


			counter = 0
			while counter < 2: # I seem to need this for correctly updating the door state
				counter += 1

				successor_rep_currdoors = calc_SR(transitions, rooms['reward'], SR_lambda) # 0.2
				successor_rep_neighbours = calc_SR(neighbours, rooms['reward'], SR_lambda) # 0.99
				successor_rep_connections = calc_SR(connections, rooms['reward'], SR_lambda) # 0.6
               
				#print "successor_rep_neighbours.shape = ", successor_rep_neighbours.shape

				#room_successors[curr_trial, :, i_subj], room_successor_value[curr_trial, :, i_subj], choice_options_NESW[curr_trial, :, i_subj], open_doors_calc_index = calc_room_successor_value(choice_NESW[:, i_subj], doors, room_at_decision[:, i_subj], avail_doors, successor_rep_currdoors, curr_trial) # SR, curr doors, lambda=0.2: Min. NLL = 127.99 (subj. 10109904)
				room_successors[curr_trial, :, i_subj], room_successor_value[curr_trial, :, i_subj], choice_options_NESW[curr_trial, :, i_subj], open_doors_calc_index = calc_room_successor_value(choice_NESW[:, i_subj], doors, room_at_decision[:, i_subj], avail_doors, successor_rep_neighbours, curr_trial) # SR, neighbours, lambda=0.99: Min.Nll = 117.45 (10109904)
				#room_successors[curr_trial, :, i_subj], room_successor_value[curr_trial, :, i_subj], choice_options_NESW[curr_trial, :, i_subj], open_doors_calc_index = calc_room_successor_value(choice_NESW[:, i_subj], doors, room_at_decision[:, i_subj], avail_doors, successor_rep_connections, curr_trial) # SR, connections, lambda=0.6: Min.Nll = 123.37 (10109904)

				open_doors_log_NESW = read_door_options_NESW(fl[i].split(), i_room_current, col)
				open_door_pos_calc_NESW = calc_door_position_NESW(rooms, doors, open_doors_calc_index, i_room_current)
				position_alldoors_NESW = calc_door_position_NESW(rooms, doors, avail_doors, i_room_current)
				# TODO:
				# 1. Calculate the door index for each of the doors from open_doors_log_NESW
				# 2. For any door which is in open_doors_log_NESW but not in open_doors_calc_index: Flip the door direction
				# 3. For any door which is in open_doors_calc_index but not in open_doors_log_NESW: Flip the door direction
				# 4. Check again?!

				excess_doors  = setdiff1d(open_door_pos_calc_NESW, open_doors_log_NESW)
				missing_doors = setdiff1d(open_doors_log_NESW, open_door_pos_calc_NESW)
				excess_doors  = excess_doors[isnan(excess_doors)==False]
				missing_doors = missing_doors[isnan(missing_doors)==False]

				# Match door positions (N,E,S,W <-> 0,1,2,3) to door index:
				nz_excess_index = nan * ones(len(excess_doors))
				excess_door_ind = nan * ones(len(excess_doors))
				for i_dir_NESW in xrange(len(excess_doors)):
					nz_excess_index[i_dir_NESW] = nonzero(int(excess_doors[i_dir_NESW]) == position_alldoors_NESW)[0]
					excess_door_ind[i_dir_NESW] = avail_doors[int(nz_excess_index[i_dir_NESW])] 

				nz_missing_index = nan * ones(len(missing_doors))
				missing_door_ind = nan * ones(len(missing_doors))
				for i_dir_NESW in xrange(len(missing_doors)):
					nz_missing_index[i_dir_NESW] = nonzero(missing_doors[i_dir_NESW] == position_alldoors_NESW)[0]
					missing_door_ind[i_dir_NESW] = avail_doors[int(nz_missing_index[i_dir_NESW])]

				# Update door state by considering excess doors and missing doors:
				doors = update_doors_with_log(doors, excess_door_ind, missing_door_ind)

				#print "room_successor_value[curr_trial, :, i_subj] = ", room_successor_value[curr_trial, :, i_subj]
				# room_successor_value[curr_trial, :, i_subj] contains at most four values - corresponding to the available neighboring rooms!

			nll_0, ptot_0 = update_nll(nll_0, ptot_0, beta_inp, [i_room_current], room_successor_value[curr_trial, :, i_subj], choice_options_NESW[curr_trial, :, i_subj], choice_NESW[curr_trial, i_subj])



	return nll_0






if __name__ == '__main__':
	# To be used with behavioral log files (pilot data for Maze task):
	#id_list_YA = [10109904]
	id_list_YA = [10109904, 10109906, 10109907, 10109912, 10109915, 10109917, 10109925, 10209908, 10209913, 10209914, 10209916, 10209921, 10209995]

	#id_list_OA = []
	id_list_OA = [20109902, 20109903, 20109909, 20109911, 20109919, 20109920, 20209901, 20209918, 20209922, 20209923, 20209924]

	filename_out = 'fit_data/SR_neighbours.txt' 
	#filename_out = 'fit_data/SR_currdoors.txt'
	#filename_out = 'fit_data/SR_connections.txt'

	file_out=open(filename_out,'w')


	for str_AB in ['A', 'B']:
		for str_YO in ['Y', 'O']:

			print str_YO + 'A, Ver.'+str_AB+': '

			if str_YO == 'Y':
				id_list = id_list_YA
			else:
				id_list = id_list_OA


			n_subjects = len(id_list)

			room_at_decision = nan * ones([500, n_subjects])
			choice_NESW = nan * ones([500, n_subjects])
			choice_options_NESW = nan * ones([500, 4, n_subjects])
			choice_options_NESW_log = nan * ones([500, 4, n_subjects])
			room_successors = nan * ones([500, 4, n_subjects])
			room_successor_value = nan * ones([500, 4, n_subjects])

			rooms = place_reward(rooms, str_AB)
			print "rooms['reward'] = ", rooms['reward']
            
			NLL_array = nan * ones(n_subjects)
			beta = nan * ones(n_subjects)                
			SR_lambda = nan * ones(n_subjects)                                            

			for i_subj in xrange(n_subjects):
				print ""                
				print "subject ", id_list[i_subj]

				# Read data from log file:

				file=open('../mazegame/pilot_data/Ver_'+str(str_AB)+'/034_MAZ_'+str(id_list[i_subj])+'/034_MAZ_'+str(id_list[i_subj])+'_'+str(str_AB)+'.txt','r')
				fl=file.readlines()
				file.close()

				param_bounds = ((0, None), (0, 1))
				guess_beta = 1.0
				guess_lambda = 0.5
				x0 = [guess_beta, guess_lambda]                   

				res = sciopt.minimize(calc_model_fit, x0, [fl, i_subj], bounds=param_bounds) 
				NLL_array[i_subj] = calc_model_fit(res.x, [fl, i_subj])#, guess_lambda])                   
				beta[i_subj] = res.x[0]
				SR_lambda[i_subj] = res.x[1]

				l_random = calc_lrandom(fl)
				rho_square = 1 - NLL_array[i_subj] / l_random

				print "sum(isnan(choice_NESW)==False) = ", sum(isnan(choice_NESW)==False)
				str_out = "Subject; " + str(id_list[i_subj]) + '_' + str_AB +"; "+ "Model_SR_neighbours; " + "beta; " + '%.2f'%(beta[i_subj]) + "; lambda; "+ '%.2f'%(SR_lambda[i_subj]) + "; NLL; "+ '%.2f'%(NLL_array[i_subj]) + "; " + "rho_square; " + '%.2f'%(rho_square) + "; " + res.message + "\n"                                                                
				print str_out
				file_out.write(str_out)


	print "beta = ", beta
	print "SR_lambda = ", SR_lambda    

	file_out.close()
