from pylab import *
from log_info import col, line

def softmax_array(state_action_val, beta):
    # Input:  State-action values [Q(s,a0), Q(s,a1),...] for all actions [a0, a1,...] available in the current state (s)
    # Output: Action probabilities [p(a0,s), p(a1,s),... ] for actions [a0, a1,...]
    #print "softmax: state_action_val = ", state_action_val
    #print "softmax: len(state_action_val) = ", len(state_action_val)
    p_choice = zeros(len(state_action_val))
    for i in xrange(len(state_action_val)):
        if isnan(state_action_val[i]) == False:
            p_choice[i] = exp(beta * state_action_val[i])
    p_choice /= sum(p_choice)
    return p_choice


def nll(beta, state_history, value_history, options, choice_history):
    # Inputs: beta:           Softmax parameter controlling the degree of randomness (0 - completely random, Inf - action with highest value is selected with probability 1)
    #         state_history:  Sequence of visited states: [s(t0), s(t1), ... , s(tN)]
    #         value_history:  State-action values for all actions available in each of these states:[[Q(s(t0), a0(t0)), Q(s(t0), a1(t0)),...], [Q(s(t1), a0(t1)), Q(s(t1), a1(t1),...], ...]
    #         choice_history: Sequence of actions chosen in each of these states: [a(t0), a(t1), ... , a(tN)]
    # Output: Negative log-likelihood: nll = -log(P(beta)), where P(beta) is the probability of choosing [a(t0), a(t1), ... , a(tN)] by softmax, given the state-action values and the softmax parameter beta
    n_trials = len(state_history)
    prob = 1.0
    if n_trials == 1:
         if isnan(choice_history) == False: # Otherwise (nan) means trivial choice -> choice probability equals 1
             i_choice = nonzero(options == choice_history)[0]
             if len(i_choice) == 0: 
                 print "Fatal error (function nll) - mismatch between choice and available options"
                 return                 
             prob = softmax_array(value_history, beta)[i_choice]
         #else: 
         #    prob *= 1.0
    else:
		for i_trial in xrange(n_trials):
		    if isnan(choice_history[i_trial]) == False:
		        i_choice = nonzero(options[i_trial, :] == choice_history[i_trial])[0]
		        prob *= softmax_array(value_history[i_trial], beta)[i_choice]
		    #else:
		    #    prob *= 1.0       
    return -log(prob), prob


def update_nll(nll_old, prob_old, beta, state, value, options, choice):
    neg_ll_curr, prob_curr = nll(beta, state, value, options, choice)
    neg_ll = nll_old + neg_ll_curr
    prob = prob_old * prob_curr
    return neg_ll, prob



def calc_lrandom(str_lines):
	# Calculates the probability / likelihood of the observed sequence of choices under the assumption of random action selection
	# This depends on the number of open doors at each step
	p_random = 1.0
	for i in range(len(str_lines)): # first data line = line 27
		if len(str_lines[i].split()) > 18 and i>line['descr']: # Excluding header lines
			# Read from log file
			curr_trial  = int(str_lines[i].split()[0])-1
			n_choices = int(str_lines[i].split()[col['exitN']]) + int(str_lines[i].split()[col['exitE']]) + int(str_lines[i].split()[col['exitS']]) + int(str_lines[i].split()[col['exitW']])
			if n_choices > 1:
			    p_random *= 1.0 / n_choices
	return -log(p_random)
