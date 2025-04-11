API reference
=============
   
   
Signal preprocessing 
--------------------

.. automodule:: myonset.use_mne
    
    .. autofunction:: apply_filter
    .. autofunction:: bipolar_ref
    .. autofunction:: drop_channels
    .. autofunction:: get_data_array
    .. autofunction:: select_channels

.. automodule:: use_mne
    
    .. autofunction:: apply_filter
    .. autofunction:: bipolar_ref
    .. autofunction:: drop_channels
    .. autofunction:: get_data_array
    .. autofunction:: select_channels


.. automodule:: use_txt
    :members: apply_filter, bipolar_ref, drop_channels, load_txt_file, select_channels
	


Signal processing and automatic detection
-----------------------------------------
   
.. automodule:: emgtools
    .. autofunction:: detector_var
	
.. automodule:: myonset.emgtools
    .. autofunction:: filtfilter
	

.. automodule:: myonset
    :members: detector_var, filtfilter, get_onset_ip, get_onset_somf, get_onsets, get_onsets_dbl_th, get_signal_max, get_signal_portions, global_var, hpfilter, integrated_profile, lpfilter, moving_avg, notch_filter, set_log_file, show_trial, signal_windows, somf, tkeo


Tools for events
----------------
   
.. automodule:: myonset
    :members: EpochEvents, Events, load_continuous, load_segmented, find_times, times
    :noindex:
	
Visualization and manual correction
-----------------------------------
   
.. automodule:: myonset
    :members: Viz
    :noindex:

.. automodule:: myonset.viz.viz_emg
    :members: VizApplication



