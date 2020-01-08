Analysis code for the Maze task
-------------------------------

1) Info about the maze environment:

initial_layout.txt
	Describes the mapping between room and door index values to locations in the maze environment



2) Files which can be run as a python "main" script:

visualize_steps.py	
	Displays a subject's sequence of decisions read from a log file. Good start for getting into the project.

fit_SR_neighbours.py
	Calculates a parameter fit for the successor representation. This is a relatively simple model, not described by Simon & Daw (2011). I think it works fine.
	Might be a good start for looking at how a parameter fit is calculated.
	The model (successor representation, SR) is briefly described by Corneil & Gestner (2015), NIPS Proceedings, section 2 (intro)

fit_planning.py
	Calculates a parameter fit for a breadth-first planning model, as in Simon & Daw (2011). There might still be some errors in the model.

fit_Q_learning.py
	Calculates a parameter fit for the temporal difference (TD) reinforcement learning (RL) algorithm, as in Simon & Daw (2011). Not sure if it works correctly.



3) Helper functions to be imported:

init_door_config.py
	Some helper functions for the maze environment

log_info.py
	Information about line numbers in the log file

maze_functions.py
	Some helper functions for the maze environment

model_fitting.py
	Some helper functions related to parameter fitting

planning.py
	Related to fitting the planning model

Q_learning.py
	Related to fitting the TD RL model
	
successor_rep.py
	Related to fitting the SR model



4) Unrelated to the model fit, for exploratory data analyses:

learning_rates.py
	Some group statistics

reaction_times.py
	Comparison of reaction times

trunc_script.py
	obsolete, can remove "trivial choice" trials with only one exit door from the log file

