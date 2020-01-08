from pylab import * # necessary?


def plot_path(path_x, path_y, imax):
	figure()
	draw_rooms()
	for it in xrange(imax):
		plot(path_x[it:it+2] + 0.03*randn(2), path_y[it:it+2] + 0.03*randn(2), color=str(it / float( imax)  ), lw = 1)
		plot(path_x[it], path_y[it], '.', color=str(it / float( len(nonzero(isnan(path_x)==0)[0] ))  )  )
	#axis([0.5, 6, 0.5, 6])
	legend(('0', '0', '1', '1'))


def draw_rooms():
	#figure()
	xymin = 0
	xymax = 6.4
	# draw horizontal lines:
	for iy in arange(xymin, xymax + (xymax-xymin)/4.0, (xymax-xymin)/4.0):
		plot([xymin,xymax],[iy,iy], 'k-')
	# draw vertical lines:
	for ix in arange(xymin, xymax + (xymax-xymin)/4.0, (xymax-xymin)/4.0):
		plot([ix, ix], [xymin,xymax], 'k-')


def plot_transitions(path_x, path_y, col_atRoom, imax):
	figure()
	for it in xrange(imax):
		subplot(4,4,it+1)
		plot(path_x[it:it+2] + 0.03*randn(2), path_y[it:it+2] + 0.03*randn(2), lw = 1)
		plot(path_x[it], path_y[it], '.')
		axis([0.5, 6, 0.5, 6])
		i_room_current = int( fl[it + 26].split()[col_atRoom] )
		print "i_room_current = ", i_room_current
		print "path_x, path_y = ", path_x[it], path_y[it]
		print "room_doors[i_room_current, :] = ", room_doors[i_room_current, :]

		if room_doors[i_room_current, 0] == 1: plot(path_x[it], path_y[it]+0.5, 'g.')
		if room_doors[i_room_current, 1] == 1: plot(path_x[it]+0.5, path_y[it], 'g.')
		if room_doors[i_room_current, 2] == 1: plot(path_x[it], path_y[it]-0.5, 'g.')
		if room_doors[i_room_current, 3] == 1: plot(path_x[it]-0.5, path_y[it], 'g.')

		ax=gca()
		ax.set_xticks([])
		ax.set_yticks([])
		title('Trial '+str(it), fontsize=8)


def plot_transition_freqs(trans_mat):
	xymin = 0.8
	xymax = 5.6
	offset = 0.2
	shorten = 0.1
	delta_xy = (xymax - xymin) / 3.0
	figure()
	subplot(121)
	matshow(trans_mat, fignum=False)
	colorbar()
	print "len(nonzero(trans_mat > 1)[0]) = ", len(nonzero(trans_mat > 1)[0])
	subplot(122)
	draw_rooms()
	for i in xrange(len(trans_mat[0,:])):
		xi, yi = unravel_index(i, (4,4))
		for j in xrange(i, len(trans_mat[:,0])):
			xj, yj = unravel_index(j, (4,4))
			if trans_mat[i,j] > 0:
				plot( [xymin + xi*delta_xy + offset, xymin + xj*delta_xy + offset], [xymin + yi*delta_xy + offset, xymin + yj*delta_xy + offset], '-', lw=5, color= 'b', alpha = trans_mat[i,j] / trans_mat.max() )
		for j in xrange(0, i):
			xj, yj = unravel_index(j, (4,4))
			if trans_mat[i,j] > 0:
				plot( [xymin + xi*delta_xy, xymin + xj*delta_xy], [xymin + yi*delta_xy - offset, xymin + yj*delta_xy - offset], '-', lw=5, color= 'r', alpha = trans_mat[i,j] / trans_mat.max() )


def plot_occupancy(occ_array):
	print "occ_array.sum() = ", occ_array.sum()
	occ_mat = zeros([4, 4])
	for i_room in xrange(len(occ_array)):
		i,j = unravel_index(i_room, (4,4))
		occ_mat[i,j] = occ_array[i_room]
	matshow(occ_mat)
	colorbar()


def in_out_freqs(trans_mat, jump_counter):
	diffsum = 0
	print "trans_mat.sum() = ", trans_mat.sum()
	print "jump_counter = ", jump_counter
	for i_room in xrange(len(trans_mat[0,:])):
		enter_sum = sum(trans_mat[:,i_room])
		exit_sum  = sum(trans_mat[i_room,:])
		diff = abs(enter_sum - exit_sum)
		diffsum += diff
		print "Room %i: Times entered: %i, Times exited: %i, diff=%i" %(i_room, enter_sum, exit_sum, diff)
	print "diffsum = ", diffsum


def plot_RT(RT_array, trans_mat, pertrial_RT, n_doors_trial):
	out_paths = zeros(4*4)
	for i_room in xrange(4*4):
		#out_transitions = sum(trans_mat, 1)
		out_paths[i_room] = len(nonzero(trans_mat[i_room, :])[0])
		if out_paths[i_room] > 4: 
			print "i_room, out_paths = ", i_room, out_paths[i_room]
	figure()
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
		print "n_doors, nanmean(pertrial_RT[i_nz]), sem = ", n_doors, nanmean(pertrial_RT[i_nz]), sem
		errorbar(n_doors, nanmean(pertrial_RT[i_nz]), sem, color='r', lw=3) 
	title('RT vs. doors per trial')
	ax2=gca()
	#subplot(133)
	#hist(pertrial_RT[nonzero(isnan(pertrial_RT)==False)], 200)
	ymax = max(ax1.axis()[3], ax2.axis()[3])	
	ax1.axis([ax1.axis()[0], ax1.axis()[1], 0, ymax])
	ax2.axis([ax2.axis()[0], ax2.axis()[1], 0, ymax])



def sample_mean_sliding(x_curr, xmean_old, n):
	xmean = 1.0/n * (x_curr + (n-1) * xmean_old)
	return xmean

# ------------------------------------------------------------------------------------------

if __name__ == "__main__":

	# To be used with behavioral log files (pilot data for Maze task):

	# YA:
	#id = 10109904
	id = 10109906
	#id = 10109907
	#id = 10109912

	# OA:
	#id = 20109902
	#id = 20109903
	#id = 20109909
	#id = 20109911

	file=open('../mazegame/pilot_data/Ver_A/034_MAZ_'+str(id)+'/034_MAZ_'+str(id)+'_A.txt','r')
	fl=file.readlines()
	file.close()


	# Parameter descriptions:
	il_desc = 25
	print fl[il_desc].split()

	# Reward sum for the last trial:
	col_rewardsum = 24
	print "%s = %s" %(fl[il_desc].split()[col_rewardsum], fl[-1].split()[col_rewardsum])

	# Jump:
	col_jump = 6


	'''#
	for i in range(len(fl)):
		if len(fl[i].split()) > 18 and i>25: # Excluding header lines
			# Number of open doors per trial:
		    #print fl[i].split()[0], sum(float_(fl[i].split()[14:18]))

			# Jump
			if fl[i].split()[col_jump] == '1':
				print "Trial %s: %s = %s" %(fl[i].split()[0], fl[il_desc].split()[col_jump], fl[i].split()[col_jump])
	'''


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
	col_atRoom = 10
	col_exitN = 14
	col_exitE = 15
	col_exitS = 16
	col_exitW = 17
	col_jump = 6
	col_x_coord = 11
	col_y_coord = 12
	col_target_room = 13
	col_RT = 21

	#print fl[il_desc].split()[col_atRoom]; print fl[il_desc].split()[col_exitN]; print fl[il_desc].split()[col_exitE]; print fl[il_desc].split()[col_exitS]; print fl[il_desc].split()[col_exitW]

	# trajectory:
	path_x = nan * ones(500)
	path_y = nan * ones(500)
	n_open_doors = nan * ones(500)
	trial_RT = nan * ones(500)
	#print fl[il_desc].split()[col_x_coord]; print fl[il_desc].split()[col_y_coord]

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
				room_RT[i_room_current] = sample_mean_sliding(curr_RT, room_RT[i_room_current], room_visits_xy[i_room_current])


			'''#
			if sum(isnan(room_doors[i_room_current, :])) ==0: # Room has been visited before
				print "Trial %s: %s = %s" %(fl[i].split()[0], fl[il_desc].split()[col_atRoom], fl[i].split()[col_atRoom])
				curr_doors = zeros(4)
				curr_doors[0] = int( fl[i].split()[col_exitN] )
				curr_doors[1] = int( fl[i].split()[col_exitE] )
				curr_doors[2] = int( fl[i].split()[col_exitS] )
				curr_doors[3] = int( fl[i].split()[col_exitW] )
				#if len( nonzero( array(room_doors[i_room_current, :]) - array(curr_doors) )[0] ) > 0:
				#	print "nonzero( array(room_doors[i_room_current, :]) - array(curr_doors) ) = ", nonzero( array(room_doors[i_room_current, :]) - array(curr_doors) )[0]
				if sum(curr_doors) <> sum(room_doors[i_room_current, :]):
					print "Previous doors, current doors = ", room_doors[i_room_current, :], curr_doors
					print "Door change?"
					flip_count += 1

			'''
			room_doors[i_room_current, 0] = int( fl[i].split()[col_exitN] ) # Exit_N
			room_doors[i_room_current, 1] = int( fl[i].split()[col_exitE] ) # Exit_E
			room_doors[i_room_current, 2] = int( fl[i].split()[col_exitS] ) # Exit_S
			room_doors[i_room_current, 3] = int( fl[i].split()[col_exitW] ) # Exit_W

		


			path_x[ curr_trial - 1] = fl[i].split()[col_x_coord]
			path_y[ curr_trial - 1] = fl[i].split()[col_y_coord]


			if curr_trial > 1 and curr_trial < 500 and curr_RT <> -999: # 500
				if fl[i].split()[col_jump] == '1':
					#print "Jump in trial %i" %(curr_trial)
					jump_count += 1
					#print "prev. coords: %s, %s" %(path_x[ curr_trial - 2], path_y[ curr_trial - 2])
					#print "current coords: %s, %s" %(path_x[ curr_trial - 1], path_y[ curr_trial - 1])
				else:
					target = int( fl[i].split()[col_target_room])
					transitions[i_room_current, target] += 1
					if directions[i_room_current, target] == -1:
						print "Trial %i: Room %i to room %i: Change of direction" %(curr_trial, i_room_current, target)
						dir_change_count += 1
					#else:
					#	print "Trial %i: Room %i to room %i" %(curr_trial, i_room_current, target)
					directions[i_room_current, target] = 1
					directions[target, i_room_current] = -1
					#if i_room_current == target:
					#	print "Trial %i: Room visited twice in a row" %(curr_trial)


	#print "flipcount = ", flip_count

	#'''#
	ion()
	#hist2d(path_x, path_y)

	#imax = len( nonzero(isnan(path_x)==0)[0] ) - 1
	imax = 16 # 400

	#plot_path(path_x, path_y, imax)

	#plot_transitions(path_x, path_y, col_atRoom, imax)

	plot_transition_freqs(transitions)

	plot_occupancy(room_visits_xy)

	in_out_freqs(transitions, jump_count)

	#for i_room in xrange(4*4):
	#	print "Room %i: room_coords_x, room_coords_y = %f, %f" %(i_room, room_coords_xy[i_room, 0], room_coords_xy[i_room, 1])

	print "room_RT = ", room_RT
	plot_occupancy(room_RT)

	#plot_RT(room_RT, transitions, trial_RT, n_open_doors)

	print "dir_change_count = ", dir_change_count

	#figure()
	#hist(n_open_doors[nonzero(isnan(n_open_doors)==False)], 3)
	#print "len(nonzero(n_open_doors==1)[0]) = ", len(nonzero(n_open_doors==1)[0])


	ioff()
	show()
	#'''


