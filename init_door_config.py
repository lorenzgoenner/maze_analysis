from pylab import *

L = 4
n_states = L*L
n_doors = 24
neighbours = zeros([n_states, n_states])
transitions = zeros([n_states, n_states])
xymin = 0.8
width = 1.6

states = {}
states['ind'] = range(n_states)
states['x'] = nan * ones(n_states)
states['y'] = nan * ones(n_states)

for i_state in xrange(n_states):
	states['x'][i_state] = mod(i_state, L) * width + xymin
	states['y'][i_state] = floor(i_state / L) * width + xymin
	
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
for i in xrange(n_states):
	for j in xrange(i, n_states):
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
doors['direction'][11] = 1
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

# Calculate transition matrix:
for i_door in xrange(n_doors):
	conns = doors['connects'][i_door]
	if doors['direction'][i_door] == 1:
		transitions[int(conns[0]), int(conns[1])] = 1
	elif doors['direction'][i_door] == -1:
		transitions[int(conns[1]), int(conns[0])] = 1

# Normalize transitions to get probabilities:
for i in xrange(n_states):
	transitions[i,:] /= sum(transitions[i,:])
	neighbours[i,:] /= sum(neighbours[i,:])

#'''#
print "states = ", states
print "neighbours = ", neighbours
print "nansum(neighbours) = ", nansum(neighbours)
#rint "doors =", doors
print "transitions = ", transitions
print "nansum(transitions) = ", nansum(transitions)
#'''































