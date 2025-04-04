.. _guide_events:

Events class and functions
==========================

What we call *event* here is a time marker, also called *trigger*, specifying the exact time positions of specific events like stimulus or response in (continuous) data recording such as EMG. 
Note that after performing the automatic detection of EMG onset(s) and offset(s), each burst onset and offset is stored in event markers, and saved in event files with the original event markers.
We will here describe the available classes and functions implemented in Myonset to make it easier to store and handle events. 
Two container objects are available for events in Myonset: 

* Events, intended to contain events of continuous data signal 
* EpochEvents containing events from data signal segmented in trials (or *epochs*)


.. _the_Events_class:

1. The ``Events`` class
-----------------------

``Events`` is our basic container object for events. It is based on the rationale that a particular event marker is defined by three information:

1. the event latency
2. the event code specifying the nature of the event (e.g., which stimulus, which response …)
3. eventually the event channel (e.g., EMG onset and offset are associated to one EMG channel)

In ``Events``, each of that three information is stored in a separated array. For instance, the event code is stored in array ``code`` and the channel is stored in array ``chan``.
Each array contains information of all event markers, a particular event being stored at the same index in all arrays: the n\ :sup:`th` event code is stored at index n in array ``code``, 
and the n\ :sup:`th` event channel is stored at index n in array ``chan``. 
The same logic is used for event latencies, which are stored in an object called ``lat`` (standing for Latency). In ``lat``, the array ``time`` contains event latencies in seconds 
and array ``sample`` contains latencies in data samples. We first describe how event latencies are stored, and then extend more on Events and EpochEvents objects.

1.1 Events latencies
^^^^^^^^^^^^^^^^^^^^
As stated above, the event markers latencies are stored in ``lat``, in both time units and data samples. 
Although redundant, it is often useful to store latencies in those two system units. ::

    from myonset import Events
    exp_evts = Events(time=[1,2,3,4,5], code=[1]*5, chan=[-1]*5, sf=1024) 
    exp_evts.lat
     > class Latency, 6 events, sf = 1024.0, sample: [   0 1024 2048 3072 4096 5120], time: [0 1 2 3 4 5]

Information contained in ``lat`` are:

* ``sf``: the sampling frequency of the events data signal, if sf is not provided, it will be asked explicitly
* ``sample``: numpy 1D array storing the events latency samples
* ``time``: numpy 1D array storing the events time latencies

Either time, sample, or both can be given to create ``lat``. If only one is given, the other is computed based on the sampling frequency. 
If both are given, it is not necessary that time and sample latencies match, but the two arrays must be of same length.

1.2 Class ``Events``
^^^^^^^^^^^^^^^^^^^^
``Events`` is the basic container object storing marker events. As said above, each event is defined by its latency, code and channel, 
stored respectively in Events.lat, Events.code and Events.chan::

    from myonset import Events
    exp_evts = Events(time=[1,1.5,1.623,1.678,3.5,3.709,3.785], code=[2,4,'onset',16,4,'onset',32],
                      chan=[-1,-1,0,-1,-1,1,-1], sf=1024) 
    exp_evts
     > class Events, 7 events, sf = 1024.0 
        latency: class Latency, 7 events, sf = 1024.0, sample: [1024 1536 1662 1718 3584 3798 3876], time: [1.    1.5   1.623 1.678 3.5   3.709 3.785] 
        code: ['2' '4' 'onset' '16' '4' 'onset' '32'] 
        chan: [-1 -1  0 -1 -1  1 -1]

Each event information is stored in ``Events.lat.time``, ``Events.lat.sample``, ``Events.code``, ``Events.chan``, at the same index across arrays: 
the code of the event occurring at time ``Events.lat.time[n]`` is given by ``Events.code[n]``. In the above example, ``exp_evts`` contain 5 marker events: 

* events of code ``2``, then ``4``, occurring respectively at 1 and 1.5 seconds (samples 1024 and 1536), for instance the occurrence of a fixation point followed by a stimulus. Note that they are associated with channel ``-1``, which is the channel number used in Myonset for event markers which are not associated to a particular channel
* event ``onset``, at time 1.623s (sample 1662), specifying in this example the onset of EMG burst on channel ``0``
* event of code ``16``, for instance a left-hand response, occurring at 1.678s
* event ``4`` again, i.e., a new stimulus appearing at 3.5s
* event ``onset``, occurring at 3.709s, this time associated with channel ``1``
* event ``32``, for instance right response at time 3.785s

The full list of methods available in ``Events`` is presented in :ref:`the table below<table_events_methods>`. We will here present briefly how to access and segment events.

To access one or several events, use the method get_events with event indices as arguments:

* one event::

    exp_evts.get_events(2)
     > class Events, 1 events, sf = 1024.0
        latency: class Latency, 1 events, sf = 1024.0, sample: [1662], time: [1.623] 
        code: ['onset'] 
        chan: [0]

* several events::

    exp_evts.get_events([1,3])
     > class Events, 2 events, sf = 1024.0 
        latency: class Latency, 2 events, sf = 1024.0, sample: [1536 1718], time: [1.5   1.678] 
        code: ['4' '16'] 
        chan: [-1 -1]
 
To find and get all events with a particular code, or associated with a particular channel, use::

    exp_evts.find_and_get_events(code=['2','4'])
     > 3 event(s) selected.
     > class Events, 3 events, sf = 1024.0 
        latency: class Latency, 3 events, sf = 1024.0, sample: [1024 1536 3584], time: [1.  1.5 3.5] 
        code: ['2' '4' '4'] 
        chan: [-1 -1 -1]

:: 

    exp_evts.find_and_get_events(chan=0)
     > 1 event(s) selected.
     > class Events, 1 events, sf = 1024.0 
        latency: class Latency, 1 events, sf = 1024.0, sample: [1662], time: [1.623] 
        code: ['onset'] 
        chan: [0]

Note that, when specifying several values for one attribute (for instance here several codes), events whose attribute is equal to either value is selected. 
If several attributes are filled however, only events satisfying all requirements are selected::

    exp_evts.find_and_get_events(code=['2','4'],chan=0)
     > Event(s) not found, nothing was selected.
     > class Events, 0 events, sf = 1024.0 
        latency: class Latency, 0 events, sf = 1024.0, sample: [], time: [] 
        code: [] 
        chan: []
		
To find events with either code ``'2'`` or ``'4'`` or channel ``0``, the user can combine several searches using the find_events functions, 
that returns the index of the searched events::

    exp_evts.find_events(code=['2','4'])
     > array([0, 1, 4], dtype=int64)
    exp_evts.find_events(chan=0)
     > array([2], dtype=int64)

    exp_evts.get_events([0,1,4,2])
     > class Events, 4 events, sf = 1024.0 
        latency: class Latency, 4 events, sf = 1024.0, sample: [1024 1536 3584 1662], time: [1.  1.5  3.5  1.623] 
        code: ['2' '4' '4' 'onset'] 
        chan: [-1 -1 -1  0]

Finally, continuous events can be segmented using the method ``segment``, returning an EpochEvents object presented below. 
For instance here, to segment on stimulus events::

    epochs_evts = exp_evts.segment(code_t0=['4'], tmin=-0.5, tmax = 1)
    > Found 2 epoch(s).

::
    
    epochs_evts
     > class EpochEvents, 2 trials, 7 events, sf = 1024.0 


.. _the_EpochEvents_class:

2. The ``EpochEvents`` class
----------------------------

The ``EpochEvents`` object is used to store segmented events or *epoch* events, i.e., events divided in fixed length segments, usually around reference event code(s), 
defined by ``code_t0`` parameter. In most cases, the ``EpochEvents`` is obtained after the segmentation of continuous events stored in an ``Events`` object. 
For instance, in the above example, events are segmented from -0.5 to 1s around each event ``'4'``. Two events ``‘4’`` are present in exp_evts, 
resulting in an EpochEvents containing 2 trials (or 2 segments). 

EpochEvents contain:

* ``list_evts_trials``: list of ``Events`` objects storing the marker events of consecutive trials. Each element of ``list_evts_trials`` is an independent Events object. Note that time latencies are now given in reference to the trial’s *code_t0* event, while sample latencies are given in reference to trial’s first sample::

    epochs_evts.list_evts_trials[0]
     > class Events, 4 events, sf = 1024.0 
        latency: class Latency, 4 events, sf = 1024.0, sample: [  0 512 638 694], time: [-0.5    0.     0.123  0.178] 
        code: ['2' '4' 'onset' '16'] 
        chan: [-1 -1  0 -1]

    epochs_evts.list_evts_trials[1]
     > class Events, 3 events, sf = 1024.0 
        latency: class Latency, 3 events, sf = 1024.0, sample: [512 726 804], time: [0.    0.209 0.285] 
        code: ['4' 'onset' '32'] 
        chan: [-1  1 -1]

* tmin: ``Latency`` object storing the starting latency of each trial
* t0: ``Latency`` object storing the time 0 latency of each trial
* tmax: ``Latency`` object storing the ending latency of each trial

::

    epochs_evts.tmin
     > class Latency, 2 events, sf = 1024.0, sample: [1024 3072], time: [1. 3.]
    epochs_evts.t0
     > class Latency, 2 events, sf = 1024.0, sample: [1536 3584], time: [1.5 3.5]


The full list of methods available in EpochEvents is presented in :ref:`the table below<table_events_methods>`. 
We here present only the method ``as_continuous``, allowing to return to continuous events, from segmented events::

    continuous_evts, trials = epochs_evts.as_continuous()
     > Checking for duplicates in events...
     > 0 event(s) removed.

The method concatenates all trials’ ``Events`` (i.e., all elements of list_evts_trials) and recompute continuous events latencies based on ``EpochEvents.tmin`` latencies. 
A new ``Events`` object is returned, containing the continuous events (``continuous_evts``) as well as a numpy array containing the trial index of each event of the continuous events. 
In the example below, the ``continuous_evts`` is equal to ``exp_evts`` above, and trials array indicate that events 0 to 3 in ``continuous_evts`` belonged to trial 0, 
and events 4 to 6 belonged to trial 1. ::

    continuous_evts
     > class Events, 7 events, sf = 1024.0 
        latency: class Latency, 7 events, sf = 1024.0, sample: [1024 1536 ... 3876], time: [1. 1.5 ... 3.785] 
        code: ['2' '4' 'onset' '16' '4' 'onset' '32'] 
        chan: [-1 -1  0 -1 -1  1 -1]
    trials
     > array([0, 0, 0, 0, 1, 1, 1])

In some cases, for instance when trial length is long, some event markers can be duplicated. 
In the example below, increasing trial duration to 2s after stimulus results in the inclusion of stimulus event of trial 1 at the end of trial 0::

    epochs_evts = exp_evts.segment(code_t0=['4'], tmin=-.5, tmax=2)
     > Found 2 epoch(s).
    epochs_evts.list_evts_trials[0]
     > class Events, 5 events, sf = 1024.0 
        latency: class Latency, 5 events, sf = 1024.0, sample: [0 512 638 694 2560], time: [-0.5 0. 0.123 0.178 2.] 
        code: ['2' '4' 'onset' '16' '4'] 
        chan: [-1 -1  0 -1 -1]

In most cases, this has no consequence for the epoch events. When switching back to continuous events using ``as_continuous`` however, duplicated events must be dropped::

    continuous_evts, trials = epochs_evts.as_continuous()
     > Checking for duplicates in events...
     > 1 event(s) removed.


By default, ``as_continuous`` keeps only the first occurrence of any duplicated event (i.e., marker events with same latency, code and channel), 
and the user is informed of the total number of duplicated events that have been deleted. 
Note that checking for duplicates across all events can take time, to deactivate this precaution and keep all events, set drop_duplic to False::

    continuous_evts, trials = epochs_evts.as_continuous(drop_duplic=False)
    continuous_evts
     > class Events, 8 events, sf = 1024.0 
        latency: class Latency, 8 events, sf = 1024.0, sample: [1024 ... 1718 3584 3584 3798 3876], time: [1. ... 1.678 3.5 3.5 3.709 3.785] 
        code: ['2' '4' 'onset' '16' '4' '4' 'onset' '32']        
        chan: [-1 -1  0 -1 -1 -1  1 -1]


On the other hand, when epochs are short, some event markers can be lost in the ``EpochEvents``. For instance, if epochs are defined from 0 to 0.150s around stimulus, several events
will not be kept in the ``EpochEvents``::

    short_epochs = exp_evts.segment(code_t0=['4'], tmin=0, tmax = 0.15)
     > Found 2 epochs
    short_epochs.list_evts_trials[0]
     > class Events, 2 events, sf = 1024.0 
        latency: class Latency, 2 events, sf = 1024.0, sample: [  0 126], time: [0.    0.123] 
        code: ['4' 'onset'] 
        chan: [-1  0]


The events not kept in ``EpochEvents`` are then lost when switching back to continuous events::

    continuous_evts = short_epochs.as_continuous()[0]
     > Checking for duplicates in events...
     > 0 event(s) removed.
    continuous_evts   
     > class Events, 3 events, sf = 1024.0 
        latency: class Latency, 3 events, sf = 1024.0, sample: [1536 1662 3584], time: [1.5   1.623 3.5  ] 
        code: ['4' 'onset' '4'] 
        chan: [-1  0 -1]


To avoid losing events, one good practice is to always combine original continuous events with the events resulting from ``as_continuous`` method. By setting the parameter ``drop_duplic`` to True, duplicated events will be removed automatically::

    continuous_evts.add_events(exp_evts, drop_duplic=True)
     > Checking for duplicates in events...
     > 3 event(s) removed.
    continuous_evts
     > class Events, 7 events, sf = 1024.0 
        latency: class Latency, 7 events, sf = 1024.0, sample: [1024 1536 1662 1718 3584 3798 3876], time: [1.    1.5   1.623 1.678 3.5   3.709 3.785] 
        code: ['2' '4' 'onset' '16' '4' 'onset' '32'] 
        chan: [-1 -1  0 -1 -1  1 -1]




3. Functions for events
-----------------------



.. _table_events_methods:

.. table:: Table ``Events`` methods


	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|     Method name   | Description                     | Main parameters and                                          |    Return              |
	|                   |                                 |       example                                                |                        |
	+===================+=================================+==============================================================+========================+
	|                                                          MANIPULATE                                                                         |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	| nb_events         |Count single events              |   exp_evts.nb_events()                                       |Number of single events |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	| sort_events       |Sort events on latency           |   exp_evts.sort_events()                                     |  Occur in place        | 
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	| copy              |Copy Events object               |   exp_evts.copy()                                            |  Events object         |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 |List of event(s) index:                                       |                        | 
	| del_events        |Delete single events             |       exp_evts.del_events([0])                               |  Occur in place        |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 |Events object:                                                |                        | 
	| add_events        |Add single events                |exp_evts.add_events(Events(sample=3,code=2,chan=-1,sf=1024))  |  Occur in place        |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |Remove events identical to a     |                                                              |                        |
	|drop_duplicates    |previous event (same code,       |             exp_evts.drop_duplicates()                       |  Occur in place        |
	|                   |channel,and latency)             |                                                              |                        |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                                                            ACCESS                                                                           |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 | List of event(s) index:                                      |Events object containing|
	| get_events        |Get the specified events         |         exp_evts.get_events([1,4])                           |specified events        |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |Find events identical to a       |                                                              |                        |	
	|  get_duplicates   |previous event (same code,       |          exp_evts.get_duplicates()                           | Indices of duplicated  |
	|                   |channel, and latency)            |                                                              | events in numpy array  |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	| find_events       |Find events satisfying the       |Events object or wanted requirements:                         | Wanted indices in      |
	|                   |specified requirements           |       stim_evts_idx = exp_evts.find_events(code=4,...)       | numpy array            |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |Get events satisfying the        |Events object or wanted requirements:                         |Events object containing| 
	|find_and_get_events|specified requirements           |      stim_evts = exp_evts.find_and_get_events(code=4,...)    |wanted events           |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |Delete events satisfying the     |Events object or wanted requirements:                         |                        | 
	|find_and_del_events|specified requirements           |             exp_evts.find_and_del_events(code=2,...)         |  Occur in place        |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                                                         SEGMENT                                                                             |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 |Reference event code:                                         |                        |
	|                   |Segment events based on          |    exp_evts.segment(code_t0=4, tmin=0, tmax=1)               |                        |
	|    segment        |reference event code (‘code_t0’),|Events indices:                                               |   EpochEvents object   |
	|                   |or specified events indices      |    exp_evts.segment(pos_events0=[2,4], tmin=0, tmax=1)       |                        |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                                                            SAVE                                                                             |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 | Filename:                                                    |                        |
	| to_csv            |Save events in a csv file        |         exp_evts.to_csv(fname,...)                           |Create a csv file       |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |Save events in a txt file,       |                                                              |                        |
	| to_txt            |corresponding to BrainVision     | Filename:                                                    |                        |
	|                   |text export format               |         exp_evts.to_txt(fname,...)                           |Create a txt file       |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |Save events in a txt file,       |                                                              |                        |
	| to_bva_vmrk       |corresponding to BrainVision     | Filename:                                                    |                        |
	|                   |vmrk format                      |         exp_evts.to_bva_vrmk(fname,...)                      |Create a vmrk file      |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |Save events in a txt file,       |                                                              |                        |
	| to_bva_markers    |corresponding to BrainVision     | Filename:                                                    |                        |
	|                   |'.Markers' format                |         exp_evts.to_bva_markers(fname,...)                   |Create a .Markers file  |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
    


.. _table_epochevents_methods:

.. table:: Table ``EpochEvents`` methods


	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|     Method name   | Description                     | Main parameters and                                          |    Return              |
	|                   |                                 |       example                                                |                        |
	+===================+=================================+==============================================================+========================+
	|                                                          MANIPULATE                                                                         |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	| nb_events         |Count single events              |              epochs_evts.nb_events()                         |Number of single events |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	| as_continuous     |"Flatten" EpochEvents and        |                                                              |Continuous Events object|
	|                   |recreate original continuous     |             epochs_evts.as_continuous()                      |and trial index of each |
	|                   |Events                           |                                                              |event                   |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                                                     MANIPULATE AND ACCESS                                                                   |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	| nb_trials         | Count trials                    |                epochs_evts.nb_trials()                       |Number or trials        |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 | Trial index:                                                 |                        | 
	| del_trial         |Delete trial events              |                epochs_evts.del_trial(0)                      |  Occur in place        | 
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 |Events object and starting, time 0 and ending trial latencies:|                        | 
	| add_trial         |Add trial events                 | epochs_evts.add_trial(Events(time=[5.5,5.65], code=[4,32],   |  Occur in place        |                           
	|                   |                                 |  chan=[-1,-1], sf=1024), latency_min, latency0, latency_max) |                        |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 |List of index:                                                | EpochEvents containing |
	| get_trials        |Get the specified trials         |       trial_epochs = epochs_evts.get_trials([0])             | specified trials       |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |Get the corresponding signal     |Data array:                                                   |3D data array containing|
	| get_data          |portions in given data array     |       data_epochs = epochs_evts.get_data(data)               |data epochs             |
	|                   |                                 |                                                              |(trials x chan x times) |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                                                            SAVE                                                                             |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |                                 | Filename:                                                    |                        |                       
	| to_csv            |Save EpochEvents in a csv file   |         epochs_evts.to_csv(fname,...)                        |Create a csv file       |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	|                   |"Flatten" EpochEvents and save   | Filename:                                                    |                        |                       
	| continuous_to_csv |continuous in a csv file         |         epochs_evts.continuous_to_csv(fname,...)             |Create a csv file       |
	+-------------------+---------------------------------+--------------------------------------------------------------+------------------------+
	

	
	
	
	



