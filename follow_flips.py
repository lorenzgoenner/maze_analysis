from pylab import *
from init_door_config import states, transitions, doors, neighbours, n_states

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

		for i_subj in xrange(n_subjects):

			file=open('../../pilot_data/Ver_'+str(str_AB)+'/034_MAZ_'+str(id_list[i_subj])+'/034_MAZ_'+str(id_list[i_subj])+'_'+str(str_AB)+'.txt','r')
			fl=file.readlines()
			file.close()


			# Parameter descriptions:
			il_desc = 25

			col_jump = 6
			col_atRoom = 10
			col_x_coord = 11
			col_y_coord = 12
			col_target_room = 13
			col_exitN = 14
			col_exitE = 15
			col_exitS = 16
			col_exitW = 17
			col_RT = 21
			col_reward = 23
			col_rewardsum = 24 	# Reward sum for the last trial
			col_steps = 25


			# trajectory:

			trial_reward = nan * ones(500)
			trial_rewardsum = nan * ones(500)
			trial_steps = nan * ones(500)

			flip_count = 0
			jump_count = 0
			dir_change_count = 0

			for i in range(len(fl)):
			#for i in range(40):
				if len(fl[i].split()) > 18 and i>25: # Excluding header lines
					i_room_current = int( fl[i].split()[col_atRoom] )

					curr_trial  = int(fl[i].split()[0])

