from pylab import *
from init_door_config import calc_transitions, draw_doors, place_reward, draw_reward, rooms, transitions, doors, neighbours, n_rooms, n_doors
from trunc_script_lg import plot_path, draw_rooms, plot_transitions
#from successor_rep import calc_SR, plot_occupancy
from Q_learning import update_Q_TD

from maze_functions import calc_agent_direction, calc_door_direction, calc_door_position_NESW, check_door_flip, coord_transform, calc_room_successor_value, calc_room_successor_value_doors, read_door_options_NESW, update_doors_with_log, calc_choice_options_NESW
from model_fitting import softmax_array, nll, update_nll, calc_lrandom
from log_info import col, line

from time import sleep

import scipy.optimize as sciopt

# Note:
# Problems during the fitting process!
# As the negative log-likelihood is minimized,
# the matrix of Q-values becomes more and more homogeneous!
# This would correspond to essentially random behavior.
# Where is the error?!


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

def calc_model_fit_Q(TD_params, fixed_params):    
	# Input: fl (Result of file.readlines())
	global doors
	global neighbours

	#beta_inp = params[0]
	#SR_lambda = params[1]    
	Q0 = TD_params[0]
	alpha = TD_params[1]
	gamma = TD_params[2]
	TD_lambda = TD_params[3]
	beta_inp = TD_params[4]
    
	#print "TD_params = ", TD_params

	Q_TD = Q0 * ones(n_doors) # Treat each door as a single action, rather than as two actions (form two different sides)
	e_traces = zeros(n_doors) # dito


	fl = fixed_params[0]
	i_subj = fixed_params[1]
   
	room_at_decision = nan * ones([500, n_subjects])
	open_door_count = nan * ones([500, n_subjects])
	choice_NESW = nan * ones([500, n_subjects])
	choice_options_NESW = nan * ones([500, 4, n_subjects])
	choice_options_NESW_log = nan * ones([500, 4, n_subjects])
	room_successors = nan * ones([500, 4, n_subjects])
	state_action_value = nan * ones([500, 4, n_subjects])


	trial_reward = nan * ones(500)
	trial_rewardsum = nan * ones(500)
	trial_steps = nan * ones(500)

	nll_0 = 0
	ptot_0 = 1

	l_random = 0.0


	for i in range(len(fl)): # first data line = line 27
	#for i in range(65): # first data line = line 27
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

			is_jump = fl[i].split()[col['jump']]

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
			while counter < 2: # 2: # I seem to need two iterations for correctly updating the door state - also for Q-learning!
				counter += 1

				#TD_params = Q0, alpha, gamma, TD_lambda, beta_inp
				#Q_TD, e_traces = update_Q_TD(Q_TD, e_traces, TD_params, rooms['reward'], curr_trial, room_at_decision[:, i_subj], i_atDoor_current, is_jump, choice_NESW[curr_trial, i_subj], avail_doors)
				#room_successors[curr_trial, :, i_subj], room_successor_value[curr_trial, :, i_subj], choice_options_NESW[curr_trial, :, i_subj], open_doors_calc_index = calc_room_successor_value(choice_NESW[:, i_subj], doors, room_at_decision[:, i_subj], avail_doors, Q_TD, curr_trial)
				state_action_value[curr_trial, :, i_subj], open_doors_calc_index = calc_room_successor_value_doors(choice_NESW[:, i_subj], doors, room_at_decision[:, i_subj], avail_doors, Q_TD, curr_trial)    
				# CAUTION - calc_room_successor_value() has been developed for the SR model, where the SR is of size 16 (one value per room)
				# CAUTION - Here, Q_TD is of size 24 (one value per door) !!!
                
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

				state_action_value[curr_trial, :, i_subj], open_doors_calc_index = calc_room_successor_value_doors(choice_NESW[:, i_subj], doors, room_at_decision[:, i_subj], avail_doors, Q_TD, curr_trial)    
                
				Q_TD, e_traces = update_Q_TD(Q_TD, e_traces, TD_params, rooms['reward'], curr_trial, room_at_decision[:, i_subj], i_atDoor_current, is_jump, choice_NESW[curr_trial, i_subj], avail_doors)
				'''#
				ion()
				draw_rooms()
				draw_doors(doors)
				#plot(Q_TD)
				ioff()
				show()
				'''
				#print "state_action_value[curr_trial, :, i_subj] = ", state_action_value[curr_trial, :, i_subj]
				choice_options_NESW[curr_trial, :, i_subj] = calc_choice_options_NESW(doors, avail_doors, room_at_decision[:, i_subj], curr_trial)
				#print "choice_options_NESW[curr_trial, :, i_subj] = ", choice_options_NESW[curr_trial, :, i_subj]


				#print "nanstd(Q_TD) = ", nanstd(Q_TD)

			#nll_0, ptot_0 = update_nll(nll_0, ptot_0, beta_inp, [i_room_current], room_successor_value[curr_trial, :, i_subj], choice_options_NESW[curr_trial, :, i_subj], choice_NESW[curr_trial, i_subj])
			nll_0, ptot_0 = update_nll(nll_0, ptot_0, beta_inp, [i_room_current], state_action_value[curr_trial, :, i_subj], choice_options_NESW[curr_trial, :, i_subj], choice_NESW[curr_trial, i_subj])

			#nll_0, ptot_0 = update_nll(nll_0, ptot_0, beta_inp, [i_room_current], Q_TD, choice_options_NESW[curr_trial, :, i_subj], choice_NESW[curr_trial, i_subj])
			#print "nll_0 = ", nll_0

	#print "nanstd(Q_TD) = ", nanstd(Q_TD)
	#print "nanstd(Q_TD) / nanmean(Q_TD) = ", nanstd(Q_TD) / nanmean(Q_TD)
	#print "Q_TD = ",Q_TD
	#print "e_traces = ", e_traces

	#print "nll_0 = ", nll_0
	#if rand()< 0.1: print "nll_0 = ", nll_0    
    
	return nll_0






if __name__ == '__main__':
	# To be used with behavioral log files (pilot data for Maze task):
	id_list_YA = [10109904]
	#id_list_YA = [10109904, 10109906, 10109907, 10109912, 10109915, 10109917, 10109925, 10209908, 10209913, 10209914, 10209916, 10209921, 10209995]

	#id_list_OA = [20109902]
	id_list_OA = [20109902, 20109903, 20109909, 20109911, 20109919, 20109920, 20209901, 20209918, 20209922, 20209923, 20209924]

	filename_out = 'fit_data/Q_learning.txt' 

	file_out=open(filename_out,'w')


	for str_AB in ['A']: #, 'B']:
	#for str_AB in ['A', 'B']:        
		for str_YO in ['Y']: #, 'O']:
		#for str_YO in ['Y', 'O']:            

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
            
			NLL_array = nan * ones(n_subjects)
			Q0 = nan * ones(n_subjects)            
			alpha = nan * ones(n_subjects)
			gamma = nan * ones(n_subjects)            
			TD_lambda = nan * ones(n_subjects)            
			beta = nan * ones(n_subjects)                

			for i_subj in xrange(n_subjects):
				print ""                
				print "subject ", id_list[i_subj]

				# Read data from log file:

				file=open('../mazegame/pilot_data/Ver_'+str(str_AB)+'/034_MAZ_'+str(id_list[i_subj])+'/034_MAZ_'+str(id_list[i_subj])+'_'+str(str_AB)+'.txt','r')
				fl=file.readlines()
				file.close()

				guess_Q0 = 2.8
				guess_alpha = 0.4
				guess_gamma = 0.8
				guess_TDlambda = 0.75
				guess_beta = 1.0
				x0 = [guess_Q0, guess_alpha, guess_gamma, guess_TDlambda, guess_beta]
				#param_bounds = ((0, None), (0, 1), (0, 1), (0, 1), (0, None))  # v1
				param_bounds = ((0, None), (0, None), (0, 1), (0, 1), (0, None))                

				res = sciopt.minimize(calc_model_fit_Q, x0, [fl, i_subj], bounds=param_bounds) 
				NLL_array[i_subj] = calc_model_fit_Q(res.x, [fl, i_subj])
				#NLL_array[i_subj] = calc_model_fit_Q(x0, [fl, i_subj])

				#'''#
				Q0[i_subj] = res.x[0]
				alpha[i_subj] = res.x[1]
				gamma[i_subj] = res.x[2]
				TD_lambda[i_subj] = res.x[3]
				beta[i_subj] = res.x[4]
				#'''

				l_random = calc_lrandom(fl)
				rho_square = 1 - NLL_array[i_subj] / l_random

				print "NLL = %.2f, rho_square = %.2f" %(NLL_array[i_subj], rho_square)

				#print "sum(isnan(choice_NESW)==False) = ", sum(isnan(choice_NESW)==False)
				str_out = "Subject; " + str(id_list[i_subj]) + '_' + str_AB +"; "+ "Model_TD_Qlearning; " + "Q0; " + '%.2f'%(Q0[i_subj]) + "; alpha; " + '%.2f'%(alpha[i_subj]) + "; gamma; " + '%.2f'%(gamma[i_subj]) + "; TDlambda; "+ '%.2f'%(TD_lambda[i_subj]) + "; beta; " + '%.2f'%(beta[i_subj]) + "; NLL; "+ '%.2f'%(NLL_array[i_subj]) + "; " + "rho_square; " + '%.2f'%(rho_square) + "; " + res.message + "\n"                                                                
				print str_out
				file_out.write(str_out)


	#print "beta = ", beta
	#print "SR_lambda = ", SR_lambda    

	file_out.close()
