How to install
==============

Dependencies
------------
Myonset toolbox requires Python 3 installation, installing Anaconda is recommended, but any other Python 3 installation should work. Most DEBut dependencies are provided with a base Anaconda environment (numpy, scipy, matplotlib, PyQt5). 
The only package that needs to be installed (when using Anaconda...) is pyqtgraph (installation instruction below).

Installing through pip/Anaconda
-------------------------------
Open the anaconda prompt (Windows: Applications / Anaconda 3 / Anaconda prompt ; Mac or linux: just start a terminal).
First, install pyqtgraph. 

With Anaconda::
    
	conda install pyqtgraph

With pip::
    
	conda install pyqtgraph
Most users will also need mne-python, on which we mainly rely to open and save files containing EMG data signal::
    
	pip install mne

Finally, install myonset, still in anaconda prompt::
    
	pip install myonset
	
	
Testing your installation
-------------------------
	
For a rapid check of your installation, run the code below::


	import numpy as np
	import myonset as myo
	 
	# Generates random signal (i.e., EMG background)
	random_signal = np.random.randn(1000)

	# Insert higher signals (i.e., EMG bursts), 
	snr = 10 # signal-to-noise ratio between signal background and bursts
	random_signal[350:450] = np.random.randn(100)*snr
	random_signal[780:800] = np.random.randn(20)*snr

	# Defines sampling frequency and generates times vector
	sf = 1000
	times = myo.times(-0.200,0.799,sf=sf)

	# Show simulated signal with detected onset(s) and offset(s) (single threshold)
	myo.show_trial(random_signal, times,sf=sf)


	#### SIGNAL PREPROCESSING ####

	# High-pass filter
	random_signal = myo.hpfilter(random_signal,sf=sf,cutoff=10)


	#### METHODS ILLUSTRATION ####
	import matplotlib.pyplot as plt

	# Compute Teager-Kaiser and plot 
	tkeo = myo.tkeo(random_signal)
	plt.figure()
	plt.plot(times,tkeo)
	plt.plot(times,random_signal)
	plt.legend(['tkeo','raw'])
	plt.title('Teager-Kaiser Energy Operator')


	# Compute Integrated Profile and plot 
	ip = myo.integrated_profile(random_signal, times)
	plt.figure()
	plt.plot(times,random_signal)
	plt.plot(times,ip-ip.mean())
	plt.legend(['signal','ip'])
	plt.title('Integrated Profile')


	#### RUN AUTOMATIC DETECTION ON EPOCHS ####

	# Define some trigger codes
	stimulus_codes = ['1']

	# Create some events triggers for simulated signal
	events = myo.Events(time=[0.2,0.7],
						code=[stimulus_codes[0], stimulus_codes[0]],
						chan = [-1,-1],
						sf=sf)

	# Segment events, time pre-stimulus is required for detection (i.e. tmin must be negative)
	tmin = -0.100
	tmax = 0.299
	times_epoch = myo.times(tmin,tmax,sf=sf)
	epochs_events = events.segment(stimulus_codes,tmin=tmin,tmax=tmax)
	epochs_signals = epochs_events.get_data(random_signal)
										
	# Run automatic detection for each epoch/trial
	for e in range(epochs_events.nb_trials()):
		
		onsets,offsets = myo.get_onsets(epochs_signals[e,0,:], times_epoch, sf=sf, method='single_threshold')

		# Put in Event structure and store in epochs_events
		onsets_events = myo.Events(sample=onsets, time=times_epoch[onsets], code=['onset']*len(onsets), chan=[0]*len(onsets), sf=sf) 
		offsets_events = myo.Events(sample=offsets, time=times_epoch[offsets], code=['offset']*len(offsets), chan=[0]*len(offsets), sf=sf) 
		epochs_events.list_evts_trials[e].add_events(onsets_events)
		epochs_events.list_evts_trials[e].add_events(offsets_events)


	#### USE VIZ TO VISUALIZE AND CORRECT AUTOMATIC DETECTION ####

	import sys

	# First recreate continuous events
	events = epochs_events.as_continuous()[0]

	# Call Viz application
	viz = myo.Viz(sys.argv)
	viz.load_data(random_signal, events, stimulus_codes,\
				  tmin=tmin, tmax=tmax,\
				  code_movable_1='onset', code_movable_2='offset')
	viz.show()    
		
	#### EXTRACT CORRECTED ONOSETS AND OFFSETS EVENTS AND SAVE ####

	corrected_events = viz.get_events()
	corrected_events.to_csv('corrected_events.csv')




