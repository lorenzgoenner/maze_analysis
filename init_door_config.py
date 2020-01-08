from pylab import *
from trunc_script_lg import plot_path, draw_rooms, plot_transitions

def calc_transitions(doors, neighbours, n_doors):
    # Calculate transition matrix:
    for i_door in xrange(n_doors):
    	conns = doors['connects'][i_door]
    	if doors['direction'][i_door] == 1:
    		transitions[int(conns[0]), int(conns[1])] = 1
    	elif doors['direction'][i_door] == -1:
    		transitions[int(conns[1]), int(conns[0])] = 1
    # Normalize transitions to get probabilities:
    for i in xrange(n_rooms):
    	transitions[i,:] /= sum(transitions[i,:])
    	neighbours[i,:] /= sum(neighbours[i,:])
    connections = 0.5*(transitions + transpose(transitions))
    return transitions, neighbours, connections


def draw_doors(doors):
    for i_door in xrange(n_doors):
        if doors['diff_x'][i_door] > 0:
            if doors['direction'][i_door] == 1:
                plot(doors['position_x'][i_door], doors['position_y'][i_door], 'b>')
            else:
                plot(doors['position_x'][i_door], doors['position_y'][i_door], 'b<')
        elif doors['diff_y'][i_door] > 0:
            if doors['direction'][i_door] == 1:
                plot(doors['position_x'][i_door], doors['position_y'][i_door], 'b^')
            else:
                plot(doors['position_x'][i_door], doors['position_y'][i_door], 'bv')

def place_reward(rooms, str_version):
    if str_version == 'A':
        rooms['reward'] = zeros(n_rooms)
        rooms['reward'][0] = 2
        rooms['reward'][3] = 3
        rooms['reward'][11] = 3
        rooms['reward'][13] = 2
    elif str_version == 'B':
        rooms['reward'] = zeros(n_rooms)        
        rooms['reward'][2] = 2
        rooms['reward'][4] = 3
        rooms['reward'][12] = 3
        rooms['reward'][15] = 2
    else: print "error - wrong version string, must be A or B"
    return rooms

def draw_reward(str_version, ax):
    if str_version == 'A':
        ax.annotate('2', xy=(0.7, 0.7), xycoords='data', fontsize=15)
        ax.annotate('2', xy=(2.3, 5.5), xycoords='data', fontsize=15)
        ax.annotate('3', xy=(5.5, 0.7), xycoords='data', fontsize=15)
        ax.annotate('3', xy=(5.5, 3.9), xycoords='data', fontsize=15)
    elif str_version == 'B':
        ax.annotate('2', xy=(3.9, 0.7), xycoords='data', fontsize=15)
        ax.annotate('2', xy=(5.5, 5.5), xycoords='data', fontsize=15)
        ax.annotate('3', xy=(0.7, 2.3), xycoords='data', fontsize=15)
        ax.annotate('3', xy=(0.7, 5.5), xycoords='data', fontsize=15)
    else: print "error - wrong version string, must be A or B"

L = 4
n_rooms = L*L
n_doors = 24
neighbours = zeros([n_rooms, n_rooms])
transitions = zeros([n_rooms, n_rooms])
connections = zeros([n_rooms, n_rooms])
xymin = 0.8
width = 1.6

rooms = {}
rooms['ind'] = range(n_rooms)
rooms['x'] = nan * ones(n_rooms)
rooms['y'] = nan * ones(n_rooms)
rooms['reward'] = zeros(n_rooms)
rooms['neighbour'] = nan * ones([n_rooms, 4])
rooms['neighbour'][0, :] = [ 1,  4,nan,nan]
rooms['neighbour'][1, :] = [ 0,  2,  5,nan]
rooms['neighbour'][2, :] = [ 1,  3,  6,nan]
rooms['neighbour'][3, :] = [ 2,  7,nan,nan]
rooms['neighbour'][4, :] = [ 0,  5,  8,nan]
rooms['neighbour'][5, :] = [ 1,  4,  6,  9]
rooms['neighbour'][6, :] = [ 2,  5,  7, 10]
rooms['neighbour'][7, :] = [ 3,  6, 11,nan]
rooms['neighbour'][8, :] = [ 4,  9, 12,nan]
rooms['neighbour'][9, :] = [ 5,  8, 10, 13]
rooms['neighbour'][10,:] = [ 6,  9, 11, 14]
rooms['neighbour'][11,:] = [ 7, 10, 15,nan]
rooms['neighbour'][12,:] = [ 8, 13,nan,nan]
rooms['neighbour'][13,:] = [ 9, 12, 14,nan]
rooms['neighbour'][14,:] = [10, 13, 15,nan]
rooms['neighbour'][15,:] = [11, 14,nan,nan]

rooms['door_list'] = nan * ones([n_rooms, 4])
rooms['door_list'][0, :] = [ 0,  3,nan,nan] # Room 0 contains doors number 0 and 3
rooms['door_list'][1, :] = [ 3,  7, 10,nan] # etc.
rooms['door_list'][2, :] = [10, 14, 17,nan]
rooms['door_list'][3, :] = [17, 21,nan,nan]
rooms['door_list'][4, :] = [ 0,  1,  4,nan]
rooms['door_list'][5, :] = [ 4,  7,  8, 11]
rooms['door_list'][6, :] = [11, 14, 15, 18]
rooms['door_list'][7, :] = [18, 21, 22,nan]
rooms['door_list'][8, :] = [ 1,  2,  5,nan]
rooms['door_list'][9, :] = [ 5,  8,  9, 12]
rooms['door_list'][10, :]= [12, 15, 16, 19]
rooms['door_list'][11, :]= [19, 22, 23,nan]
rooms['door_list'][12, :]= [ 2,  6,nan,nan]
rooms['door_list'][13, :]= [ 6,  9, 13,nan]
rooms['door_list'][14, :]= [13, 16, 20,nan]
rooms['door_list'][15, :]= [20, 23,nan,nan]
for i_room in xrange(n_rooms):
	rooms['x'][i_room] = mod(i_room, L) * width + xymin
	rooms['y'][i_room] = floor(i_room / L) * width + xymin
	
#'''#
neighbours[0,1] = 1
neighbours[0,4] = 1
neighbours[1,2] = 1
neighbours[1,5] = 1
neighbours[2,3] = 1
neighbours[2,6] = 1
neighbours[3,7] = 1
neighbours[4,5] = 1
neighbours[4,8] = 1
neighbours[5,6] = 1
neighbours[5,9] = 1
neighbours[6,7] = 1
neighbours[6,10] = 1
neighbours[7,11] = 1
neighbours[8,9] = 1
neighbours[8,12] = 1
neighbours[9,10] = 1
neighbours[9,13] = 1
neighbours[10,11] = 1
neighbours[10,14] = 1
neighbours[11,15] = 1
neighbours[12,13] = 1
neighbours[13,14] = 1
neighbours[14,15] = 1
# Apply symmetry:
for i in xrange(n_rooms):
	for j in xrange(i, n_rooms):
		if neighbours[i,j] == 1:
			neighbours[j,i] = 1
#'''

doors = {}
doors['ind'] = range(n_doors)
doors['connects'] = nan * ones([n_doors, 2])
doors['connects'][0] = [0, 4]
doors['connects'][1] = [4, 8]
doors['connects'][2] = [8, 12]
doors['connects'][3] = [0, 1] 
doors['connects'][4] = [4, 5]
doors['connects'][5] = [8, 9]
doors['connects'][6] = [12,13]
doors['connects'][7] = [1, 5]
doors['connects'][8] = [5, 9]
doors['connects'][9] = [9, 13]
doors['connects'][10]= [1, 2]
doors['connects'][11]= [5, 6]
doors['connects'][12]= [9,10]
doors['connects'][13]= [13,14]
doors['connects'][14]= [2, 6]
doors['connects'][15]= [6,10]
doors['connects'][16]= [10,14]
doors['connects'][17]= [2,3]
doors['connects'][18]= [6,7]
doors['connects'][19]= [10,11]
doors['connects'][20]= [14,15]
doors['connects'][21]= [3, 7]
doors['connects'][22]= [7,11]
doors['connects'][23]= [11,15]


doors['direction'] = nan * ones(n_doors) # Direction = 1 indicates that a transition is possible in the order of the 'connects' list; -1 indicates the reverse direction
doors['direction'][0] = -1
doors['direction'][1] = -1
doors['direction'][2] = -1
doors['direction'][3] = 1
doors['direction'][4] = 1
doors['direction'][5] = -1
doors['direction'][6] = -1
doors['direction'][7] = 1 # Caution, don't forget to set the right door state at the beginning - "no backtracking"!
doors['direction'][8] = 1 
doors['direction'][9] = -1
doors['direction'][10] = -1
doors['direction'][11] = 1 # 
doors['direction'][12] = 1
doors['direction'][13] = -1
doors['direction'][14] = -1
doors['direction'][15] = 1
doors['direction'][16] = 1
doors['direction'][17] = -1
doors['direction'][18] = -1
doors['direction'][19] = -1
doors['direction'][20] = 1
doors['direction'][21] = -1
doors['direction'][22] = -1
doors['direction'][23] = -1


doors['position_x'] = nan * ones(n_doors)
doors['position_y'] = nan * ones(n_doors)
doors['diff_x'] = nan * ones(n_doors) 
doors['diff_y'] = nan * ones(n_doors)
for i_door in xrange(n_doors):
    doors['position_x'][i_door] = 0.5*(rooms['x'][int(doors['connects'][i_door][0])] + rooms['x'][int(doors['connects'][i_door][1])])
    doors['position_y'][i_door] = 0.5*(rooms['y'][int(doors['connects'][i_door][0])] + rooms['y'][int(doors['connects'][i_door][1])])
    doors['diff_x'][i_door] = rooms['x'][int(doors['connects'][i_door][1])] - rooms['x'][int(doors['connects'][i_door][0])] # This indicates the change in coordinates when passing through the door in the order of the 'connects' list (direction=1)
    doors['diff_y'][i_door] = rooms['y'][int(doors['connects'][i_door][1])] - rooms['y'][int(doors['connects'][i_door][0])]

transitions, neighbours, connections = calc_transitions(doors, neighbours, n_doors)

if __name__ == "__main__":

	#'''#
	print "rooms = ", rooms
	print "neighbours = ", neighbours
	print "nansum(neighbours) = ", nansum(neighbours)
	print "doors =", doors
	print "transitions = ", transitions
	print "nansum(transitions) = ", nansum(transitions)
	#'''

	ion()
	draw_rooms()
	draw_doors(doors)
	#matshow(transitions)
	ioff()
	show()






























