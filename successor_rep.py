from pylab import * 
from init_door_config import rooms, transitions, doors, neighbours, n_rooms



def plot_occupancy(occ_array):
	occ_mat = zeros([4, 4])
	for i_room in xrange(len(occ_array)):
		i,j = unravel_index(i_room, (4,4))
		occ_mat[i,j] = occ_array[i_room]
	matshow(occ_mat, fignum=False, origin='lower')
	#colorbar()


def calc_SR(transitions, reward, discount_gamma):
# Successor representation: See, e.g, Corneil & Gerstner (2015), NIPS
# Computation of value (v) for each state, based on a reward vector (r) and a transition matrix (P): 
# (gamma - discount factor)
#
# v = r + gamma*P*r + gamma^2*P^2*r + gamma^3*P^3*r + ...

	n_reps = 20
	prmax = 1.0
	valSR = zeros(len(reward))
	for i_rep in xrange(n_reps):
		if i_rep==0:
			valSR[:] = reward
		elif i_rep==1:
			prod = discount_gamma * dot(transitions, reward)	# Using directional doors
			valSR += prod
		else:
			prod = discount_gamma * dot(transitions, prod)	# Using directional doors
			valSR += prod
			prmax = prod.max()
		if prmax < 1e-3: break
	return valSR


if __name__ == '__main__':

	# To be used with behavioral log files (pilot data for Maze task):
	id_list_YA = [10109904]

	#id_list_YA = [10109904, 10109906, 10109907, 10109912, 10109915, 10109917, 10109925, 10209908, 10209913, 10209914, 10209916, 10209921, 10209995]

	#id_list_OA = [20109902, 20109903, 20109909, 20109911, 20109919, 20109920, 20209901, 20209918, 20209922, 20209923, 20209924]

	mean_rewsum_4groups = zeros([2, 2, 500])
	mean_rewcount_4groups = zeros([2, 2])
	mean_rewsize_4groups = zeros([2, 2])

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

				file=open('../mazegame/pilot_data/Ver_'+str(str_AB)+'/034_MAZ_'+str(id_list[i_subj])+'/034_MAZ_'+str(id_list[i_subj])+'_'+str(str_AB)+'.txt','r')
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
						curr_reward = float(fl[i].split()[col_reward])
						curr_rewsum = float(fl[i].split()[col_rewardsum])  
						if curr_reward > 0:
							curr_steps  = float(fl[i].split()[col_steps])  
							trial_steps[curr_trial - 1] = curr_steps
							trial_steps_allsubj[curr_trial - 1, i_subj] = curr_steps

						if curr_trial > 1 and curr_trial < 500: # and curr_RT <> -999:
							trial_reward[curr_trial - 1] = curr_reward
							trial_reward_allsubj[curr_trial - 1, i_subj] = trial_reward[curr_trial - 1]

							trial_rewardsum[curr_trial - 1] = curr_rewsum
							trial_rewardsum_allsubj[curr_trial - 1, i_subj] = trial_rewardsum[curr_trial - 1]



				# Finished looping across trials for one subject


			# Finished looping across subjects within a group
			ion()


	reward_vec_verA = zeros(n_rooms)	
	#'''#
	reward_vec_verA[0] = 2
	reward_vec_verA[3] = 3
	reward_vec_verA[11] = 3
	reward_vec_verA[13] = 2
	#'''
	# TEST:
	#reward_vec_verA[3] = 3
	#reward_vec_verA[0] = 2



	ion()
	n_reps = 20
	val = reward_vec_verA
	discount_gamma = 0.7 # 0.9 # 0.7
	#mat_prod = dot

	delta = 4 # 1


	#matshow(transitions)
	#colorbar()
	#figure()
	#matshow(neighbours)
	#figure()



	#SR = calc_SR(transitions, reward_vec_verA, discount_gamma)
	#print "SR = ", SR
	#figure()
	subplot(211)
	plot_occupancy(calc_SR(transitions, reward_vec_verA, discount_gamma))
	title('Successor representation (unidirectional)')
	colorbar()
	#figure()
	subplot(212)
	plot_occupancy(calc_SR(neighbours, reward_vec_verA, discount_gamma))
	title('Successor representation (symmetric)')
	colorbar()

	savefig('plots/successor_rep.png')

	ioff()
	show()


























