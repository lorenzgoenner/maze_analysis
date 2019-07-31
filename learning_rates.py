from pylab import * # necessary?


def plot_reward_single(_trial_rewardsum_allsubj):
	for i_subj in xrange(len(_trial_rewardsum_allsubj[0,:])):
		plot(_trial_rewardsum_allsubj[:, i_subj])
	xlabel('Trial')
	ylabel('Reward sum')
	axis([axis()[0], axis()[1], 0, 350])

def mean_rewardsum(_trial_rewardsum_allsubj):
	subj_mean_rewsum = mean(_trial_rewardsum_allsubj, 1)
	return subj_mean_rewsum

def plot_meanrewsum(_mean_rewsum_4groups):
	figure()		
	plot(mean_rewsum_4groups[0,0,:])
	plot(mean_rewsum_4groups[1,0,:])
	plot(mean_rewsum_4groups[0,1,:])
	plot(mean_rewsum_4groups[1,1,:])
	legend(('YA, Ver.A','YA, Ver.B', 'OA, Ver.A', 'OA, Ver.B'))

def mean_rewardcount(_trial_rewardsum_allsubj):
	subj_mean_rewsum = mean(_trial_rewardsum_allsubj, 1)
	return subj_mean_rewsum


# ------------------------------------------------------------------------------------------

# To be used with behavioral log files (pilot data for Maze task):

id_list_YA = [10109904, 10109906, 10109907, 10109912, 10109915, 10109917, 10109925, \
		   10209908, 10209913, 10209914, 10209916, 10209921, 10209995]

id_list_OA = [20109902, 20109903, 20109909, 20109911, 20109919, 20109920, \
				20209901, 20209918, 20209922, 20209923, 20209924]

mean_rewsum_4groups = zeros([2, 2, 500])
mean_rewcount_4groups = zeros([2, 2])
mean_rewsize_4groups = zeros([2, 2])

for str_AB in ['A', 'B']:
	for str_YO in ['Y', 'O']:

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

			#reward_count = len(nonzero(trial_reward_allsubj[:, i_subj])[0])

			# Finished looping across trials for one subject
		nz_ind = nonzero(trial_reward_allsubj[:, :])
		reward_count = len(nz_ind[0])
		reward_size = nanmean(trial_reward_allsubj[nz_ind])
		nz_ind_steps = nonzero(trial_steps_allsubj[:, :])
		steps = nanmean(trial_steps_allsubj[nz_ind_steps])
		print "reward_count = ", reward_count
		print "reward_size = ", reward_size
		print "steps = ", steps

		# Finished looping across subjects within a group
		ion()

	
		#figure()
		#plot_reward_single(trial_rewardsum_allsubj)
		#savefig('plots/rewsum_'+str_YO+'A_Ver'+str_AB+'.png')

		mean_rewsum_4groups[int(str_AB == 'B'), int(str_YO == 'O'), : ] = mean_rewardsum(trial_rewardsum_allsubj)
		#mean_rewcount_4groups[int(str_AB == 'B'), int(str_YO == 'O'), : ] =



plot_meanrewsum(mean_rewsum_4groups)
savefig('plots/mean_rewsum_allgroups.png')


ioff()
show()
























