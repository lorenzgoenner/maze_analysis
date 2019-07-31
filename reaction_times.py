from pylab import * # necessary?



def plot_occupancy(occ_array):
	print "occ_array.sum() = ", occ_array.sum()
	occ_mat = zeros([4, 4])
	for i_room in xrange(len(occ_array)):
		i,j = unravel_index(i_room, (4,4))
		occ_mat[i,j] = occ_array[i_room]
	matshow(occ_mat)
	colorbar()


def plot_RT(RT_array, trans_mat, pertrial_RT, n_doors_trial):
	out_paths = zeros(4*4)
	for i_room in xrange(4*4):
		#out_transitions = sum(trans_mat, 1)
		out_paths[i_room] = len(nonzero(trans_mat[i_room, :])[0])
		if out_paths[i_room] > 4: 
			print "i_room, out_paths = ", i_room, out_paths[i_room]
	#figure()
	#plot(out_transitions, RT_array, '.')
	subplot(121)
	plot(out_paths, RT_array, '.')
	title('RT vs. total no. of doors per room')	
	ax1=gca()
	subplot(122)
	plot(n_doors_trial + 0.05*randn(len(n_doors_trial)), pertrial_RT, '.')
	for n_doors in xrange(1, 4):
		i_nz = nonzero(n_doors_trial == n_doors)[0]
		print "n_doors = %i, mean RT = %f" %(n_doors, nanmean(pertrial_RT[i_nz]))
		sem = nanstd(pertrial_RT[i_nz]) / sqrt(len(i_nz))
		plot(n_doors, nanmean(pertrial_RT[i_nz]), 'rx')
		#print "n_doors, nanmean(pertrial_RT[i_nz]), sem = ", n_doors, nanmean(pertrial_RT[i_nz]), sem
		errorbar(n_doors, nanmean(pertrial_RT[i_nz]), sem, color='r', lw=3) 
	title('RT vs. doors per trial')
	ax2=gca()
	#subplot(133)
	#hist(pertrial_RT[nonzero(isnan(pertrial_RT)==False)], 200)
	ymax = max(ax1.axis()[3], ax2.axis()[3])	
	ax1.axis([ax1.axis()[0], ax1.axis()[1], 0, ymax])
	ax2.axis([ax2.axis()[0], ax2.axis()[1], 0, ymax])

def plot_RT_pooled(pertrial_RT, subj_id, pertrial_RT_all, str_verAB, str_OY):
	#figure(figsize=(2,6))
	subplot(121)
	plot(randn(len(pertrial_RT)), pertrial_RT, '.')
	ax1=gca()
	ax1.set_xticks([])
	#xlabel('Subject '+str(subj_id))
	xlabel('Pooled across subjects, Ver.'+str(str_verAB)+', '+str_OY+'A')
	ylabel('RT [ms]')
	axis([axis()[0], axis()[1], 0, 2000])


def sample_mean_sliding(x_curr, xmean_old, n):
	xmean = 1.0/n * (x_curr + (n-1) * xmean_old)
	return xmean

# ------------------------------------------------------------------------------------------

# To be used with behavioral log files (pilot data for Maze task):

# YA:
#id = 10109904
id = 10109906
#id = 10109907
#id = 10109912

id_list_YA = [10109904, 10109906, 10109907, 10109912, 10109915, 10109917, 10109925, \
		   10209908, 10209913, 10209914, 10209916, 10209921, 10209995]

id_list_OA = [20109902, 20109903, 20109909, 20109911, 20109919, 20109920, \
				20209901, 20209918, 20209922, 20209923, 20209924]

# OA:
#id = 20109902
#id = 20109903
#id = 20109909
#id = 20109911


str_AB = 'A' # 'B' # 
str_YO = 'Y' # 'O' # 

if str_YO == 'Y':
	id_list = id_list_YA
else:
	id_list = id_list_OA


n_subjects = len(id_list)

trial_RT_allsubj = nan * ones([500, n_subjects])

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
	col_rewardsum = 24 	# Reward sum for the last trial


	# Jump:



	# Test for door flips - store the last available exit (and entry) for each room:
	# Approach: 
	# Only those available doors should be stored / compared which weren't used as the previous entry
	# - this requires knowledge of the maze structure / door indexes...
	# Alternative:
	# If the number of available doors increases or decreases, this is a strong indicator for
	# a door-flip!
	# Two independent door-flips will rarely occur in the same room close in time.
	# Problem:
	# I would "count" door-flips for all rooms containing the respective door which has flipped!

	# Alternative approach:
	# Keep a list of "previous" rooms from which the current room was entered (a maximum of 4),
	# and of "successor" rooms. (Track trial number?)
	# A door flip can be detected
	# when there has been both a transition from room x to room y and from y to x!


	room_doors = nan * ones([4*4, 4])
	prev_room = nan * ones([4*4, 4])
	next_room = nan * ones([4*4, 4])



	# trajectory:
	path_x = nan * ones(500)
	path_y = nan * ones(500)
	n_open_doors = nan * ones(500)
	trial_RT = nan * ones(500)

	transitions = zeros([4*4, 4*4])
	directions = zeros([4*4, 4*4])
	#room_coords_xy = nan * ones([4*4, 2])
	room_visits_xy = zeros(4*4)
	room_coords_xy = zeros([4*4, 2])
	room_RT = zeros(4*4)

	flip_count = 0
	jump_count = 0
	dir_change_count = 0

	for i in range(len(fl)):
	#for i in range(40):
		if len(fl[i].split()) > 18 and i>25: # Excluding header lines
			i_room_current = int( fl[i].split()[col_atRoom] )

			curr_trial = int(fl[i].split()[0])
			curr_RT =  float(fl[i].split()[col_RT])

			if curr_trial > 1 and curr_trial < 500 and curr_RT <> -999:
				# Jump trials must be excluded?! A 'jump trial' means that the transition from the previous room occurred by teleportation
				prev_room[i_room_current, :] = int( fl[i-1].split()[col_atRoom] )
				next_room[i_room_current, :] = int( fl[i+1].split()[col_atRoom] )

				curr_doors = zeros(4)
				curr_doors[0] = int( fl[i].split()[col_exitN] )
				curr_doors[1] = int( fl[i].split()[col_exitE] )
				curr_doors[2] = int( fl[i].split()[col_exitS] )
				curr_doors[3] = int( fl[i].split()[col_exitW] )

				n_open_doors[curr_trial - 1] = sum(curr_doors)

				room_visits_xy[i_room_current] += 1
				room_coords_xy[i_room_current, 0] = sample_mean_sliding(path_x[ curr_trial - 1], room_coords_xy[i_room_current, 0], room_visits_xy[i_room_current])
				room_coords_xy[i_room_current, 1] = sample_mean_sliding(path_y[ curr_trial - 1], room_coords_xy[i_room_current, 1], room_visits_xy[i_room_current])
				trial_RT[curr_trial - 1] = curr_RT
				trial_RT_allsubj[curr_trial - 1, i_subj] = trial_RT[curr_trial - 1]
				room_RT[i_room_current] = sample_mean_sliding(curr_RT, room_RT[i_room_current], room_visits_xy[i_room_current])


				room_doors[i_room_current, 0] = int( fl[i].split()[col_exitN] ) # Exit_N
				room_doors[i_room_current, 1] = int( fl[i].split()[col_exitE] ) # Exit_E
				room_doors[i_room_current, 2] = int( fl[i].split()[col_exitS] ) # Exit_S
				room_doors[i_room_current, 3] = int( fl[i].split()[col_exitW] ) # Exit_W

		


			path_x[ curr_trial - 1] = fl[i].split()[col_x_coord]
			path_y[ curr_trial - 1] = fl[i].split()[col_y_coord]


			if curr_trial > 1 and curr_trial < 500 and curr_RT <> -999:
				if fl[i].split()[col_jump] == '1':
					jump_count += 1
				else:
					target = int( fl[i].split()[col_target_room])
					transitions[i_room_current, target] += 1
					if directions[i_room_current, target] == -1:
						dir_change_count += 1
					directions[i_room_current, target] = 1
					directions[target, i_room_current] = -1


	ion()

	if i_subj==n_subjects-1:	
		#plot_RT(room_RT, transitions, trial_RT, n_open_doors)
		plot_RT(room_RT, transitions, trial_RT_allsubj, n_open_doors)
		#savefig('plots/roomRT_'+str_YO+'A_Ver'+str_AB+'.png')


	#plot_RT_pooled(trial_RT, id, trial_RT_allsubj, str_AB, str_YO)


'''#
subplot(122)
RT_data_allsubj = trial_RT_allsubj[nonzero(isnan(trial_RT_allsubj)==False)]
hist(reshape(RT_data_allsubj, prod(RT_data_allsubj.shape)), 100, orientation='horizontal')#, histtype='step')
xlabel('Count')
axis([axis()[0], axis()[1], 0, 2000])

#savefig('plots/RT_'+str_YO+'A_Ver'+str_AB+'.png')
'''

ioff()
show()
#'''























