from pylab import *
from init_door_config import calc_transitions, draw_doors, place_reward, draw_reward, rooms, transitions, doors, neighbours, n_rooms, n_doors
from trunc_script_lg import draw_rooms

from maze_functions import calc_agent_direction, check_door_flip, coord_transform

from time import sleep



def draw_agent_pos(room_index, door_index):
    # Plotting routine
    x_ag, y_ag = rooms['x'][room_index], rooms['y'][room_index]
    x_door, y_door = doors['position_x'][door_index], doors['position_y'][door_index]
    if x_door == x_ag:
        if y_door > y_ag:
            plot(rooms['x'][room_index], rooms['y'][room_index], 'gv', ms=12)
        elif y_door < y_ag:
            plot(rooms['x'][room_index], rooms['y'][room_index], 'g^', ms=12)
    elif y_door == y_ag:
        if x_door > x_ag:
            plot(rooms['x'][room_index], rooms['y'][room_index], 'g<', ms=12)
        elif x_door < x_ag:
            plot(rooms['x'][room_index], rooms['y'][room_index], 'g>', ms=12)




if __name__ == '__main__':
	# To be used with behavioral log files (pilot data for Maze task):
	id_list_YA = [10109904]

	#id_list_YA = [10109904, 10109906, 10109907, 10109912, 10109915, 10109917, 10109925, 10209908, 10209913, 10209914, 10209916, 10209921, 10209995]

	#id_list_OA = [20109902, 20109903, 20109909, 20109911, 20109919, 20109920, 20209901, 20209918, 20209922, 20209923, 20209924]


	for str_AB in ['A']: #, 'B']:
		for str_YO in ['Y']: #, 'O']:

			print str_YO + 'A, Ver.'+str_AB+': '

			if str_YO == 'Y':
				id_list = id_list_YA
			else:
				id_list = id_list_OA


			n_subjects = len(id_list)

			trial_reward_allsubj = nan * ones([500, n_subjects])
			trial_rewardsum_allsubj = nan * ones([500, n_subjects]) 
			trial_steps_allsubj = nan * ones([500, n_subjects])
			open_door_count = nan * ones([500, n_subjects])
			room_at_decision = nan * ones([500, n_subjects])
			choice_NESW = nan * ones([500, n_subjects])

			choice_options_NESW = nan * ones([500, 4, n_subjects])
			choice_options_NESW_log = nan * ones([500, 4, n_subjects])
			room_successors = nan * ones([500, 4, n_subjects])
			room_successor_value = nan * ones([500, 4, n_subjects])

			rooms = place_reward(rooms, str_AB)

			for i_subj in xrange(n_subjects):

				file=open('../mazegame/pilot_data/Ver_'+str(str_AB)+'/034_MAZ_'+str(id_list[i_subj])+'/034_MAZ_'+str(id_list[i_subj])+'_'+str(str_AB)+'.txt','r')
				fl=file.readlines()
				file.close()


				# Parameter descriptions:
				il_desc = 25

				col_jump = 6
				col_atDoor = 9
				col_atRoom = 10
				col_x_coord = 11
				col_y_coord = 12
				col_target_room = 13
				col_exitN = 14
				col_exitE = 15
				col_exitS = 16
				col_exitW = 17
				col_response_key = 20
				col_RT = 21
				col_reward = 23
				col_rewardsum = 24 	# Reward sum for the last trial
				col_steps = 25
				col_door0 = 26

				# trajectory:

				trial_reward = nan * ones(500)
				trial_rewardsum = nan * ones(500)
				trial_steps = nan * ones(500)

				flip_count = 0
				jump_count = 0
				dir_change_count = 0


				for i in range(len(fl)):
					if len(fl[i].split()) > 18 and i>25: # Excluding header lines
						# Read from log file
						curr_trial  = int(fl[i].split()[0])-1
						i_room_current = int( fl[i].split()[col_atRoom] )
						i_atDoor_current = int( fl[i].split()[col_atDoor] )
						room_at_decision[curr_trial, i_subj] = i_room_current
						door_flip_data = fl[i].split()[col_door0 : col_door0 + 23]
						resp_key_LSR = fl[i].split()[col_response_key] # is one of 1,2,3 (left, straight ahead, right)
						open_door_count[curr_trial, i_subj] = int(fl[i].split()[col_exitN]) + int(fl[i].split()[col_exitE]) + int(fl[i].split()[col_exitS]) + int(fl[i].split()[col_exitW])
						agent_dir_NESW = calc_agent_direction(rooms, doors, i_room_current, i_atDoor_current)
						if open_door_count[curr_trial, i_subj] > 1:
							choice_NESW[curr_trial, i_subj] = coord_transform(resp_key_LSR, agent_dir_NESW) # Default value is nan for "trivial" choices with only one door

						# Visualize current state
						clf()
						draw_rooms()
						draw_doors(doors)
						draw_agent_pos(i_room_current, i_atDoor_current)
						ax=gca()
						draw_reward(str_AB, ax)
						# Update door state - before or after calculating neighbours and values?!
						doors = check_door_flip(door_flip_data, doors) # Currently obsolete because I will compare the door state with the log further below?!
						transitions, neighbours, connections = calc_transitions(doors, neighbours, n_doors) 
						pause(0.5)
						clf()
						# Redraw
						draw_rooms()
						draw_doors(doors)
						draw_agent_pos(i_room_current, i_atDoor_current)
						ax=gca()
						draw_reward(str_AB, ax)
						pause(0.5)

			ioff()
			show()

