# -*- coding: utf-8 -*-
"""
Created on Mon Mar 19 16:24:35 2018

@author: Laure Spieser and Boris Burle
Laboratoire de Neurosciences Cognitives
UMR 7291, CNRS, Aix-Marseille Université
3, Place Victor Hugo
13331 Marseille cedex 3

This file is part of Myonset.

Myonset is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Myonset is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Myonset. If not, see <https://www.gnu.org/licenses/>.
"""   


from .utils import utilsfunc
from . import latency 

def load_continuous(fname, sep=',', sf=None, col_sample=None, col_time=None, col_code=None, \
                    col_chan=None, headerlines=1, bottomlines=0):
    """Load continuous events.

    Load continuous events from text file fname. Fname must contain at least:
    - one column containing events samples or events times
    - one column containing events code
    - one column containing events channel

    Additional columns in fname can contain the events' trial index.

    Parameters
    -----------
    fname : str
        Name of the file to load.
    sep : str
        Separator between columns (default ",").
    sf : int
        Sampling frequency (default None).
    col_sample : int
        The column number containing events time sample (default None).
    col_time : int
        The column number containing events time (default None).
    col_code : int
        The column number containing events code (default None).
    col_chan : int
        The column number containing events channel name/number (default None).
    headerlines:
        Number of headerlines to skip (default 1).
    bottomlines : int
        Number of bottomlines to skip (default 0).

    Returns
    -------
    class Events
        Events object containing read events.
    """
    f = open(fname, 'r')
    evt_txt = f.read()
    f.close()

    evt_list = evt_txt.split('\n')[headerlines:]
    evt_list = evt_list[:len(evt_list)-bottomlines]
    while '' in evt_list:
        evt_list.remove('')

    list_trial = [None, None, None, None, None]
    idx_sample = 0
    idx_time = 1
    idx_code = 2
    idx_chan = 3
    if col_sample is not None:
        list_trial[idx_sample] = []
    if col_time is not None:
        list_trial[idx_time] = []
    if col_code is not None:
        list_trial[idx_code] = []
    if col_chan is not None:
        list_trial[idx_chan] = []

    r = 0
    while r < len(evt_list):

        line = evt_list[r].split(sep)

        if col_sample is not None:
            list_trial[idx_sample].append(utilsfunc.try_int(line[col_sample]))
        if col_time is not None:
            list_trial[idx_time].append(float(line[col_time]))
        if col_code is not None:
            list_trial[idx_code].append(utilsfunc.try_int(line[col_code]))
        if col_chan is not None:
            list_trial[idx_chan].append(utilsfunc.try_int(line[col_chan]))

        r += 1

    return Events(sample=list_trial[idx_sample], time=list_trial[idx_time],\
                  code=list_trial[idx_code], chan=list_trial[idx_chan], sf=sf)


def load_segmented(fname, headerlines=1, sep=',', sf=None,\
                   col_sample=None, col_time=None, col_code=None, col_chan=None,\
                   col_trial_idx=None, \
                   col_tmin_sample=None, col_tmin_time=None,\
                   col_t0_sample=None, col_t0_time=None, \
                   col_tmax_sample=None, col_tmax_time=None):
    """Load segmented events.

    Load segmented events from text file fname. Fname must contain at least:
    - one column containing events samples or events times
    - one column containing events code
    - one column containing events channel
    - one column containing trial index

    Additional columns can contain the time of reference of each trial in the
    corresponding continuous raw file:
    - the sample corresponding to trial's start time in continuous (tmin sample)
    - the time corresponding to trial's start time in continuous (tmin time)
    - the sample corresponding to trial's time 0 in continuous (t0 sample)
    - the time corresponding to trial's time 0 in continuous (t0 time)
    - the sample corresponding to trial's end time in continuous (tmax sample)
    - the time corresponding to trial's end time in continuous (tmax time)

    It is necessary to provide sampling frequency.

    Parameters
    -----------
    fname : str
        Name of the file to load.
    headerLines : int
        Number of headerlines to skip (default 1).
    sep : str
        Separator between columns (default ",").
    sf : int
        Sampling frequency (default None).
    col_code : int
        The column number containing events code (default None).
    col_sample : int
        The column number containing events time sample (default None).
    col_sample : int
        The column number containing events time (default None).
    col_chan : int
        The column number containing events channel name/number (default None).
    col_trial_idx : int
        The column number containing trial index (default None).
    col_tmin_sample: int
        The column number containing sample of trial's start time (default None).
    col_tmin_time : int
        The column number containing time of trial's start time (default None).
    col_t0_sample : int
        The column number containing sample of trial's time 0 (default None).
    col_t0_time : int
        The column number containing time of trial's time 0 (default None).
    col_tmax_sample: int
        The column number containing sample of trial's end time (default None).
    col_tmax_time : int
        The column number containing time of trial's end time (default None).

    Returns
    -------
    class EpochEvents
        EpochEvents object containing read events.
    """
    f = open(fname, 'r')
    evt_txt = f.read()
    f.close()

    evt_list = evt_txt.split('\n')[headerlines:]
    evt_list.remove('')

    try:
        col_trial_idx = int(col_trial_idx)
    except:
        print('Trial index column is necessary, provide valid integer value for col_trialIdx.')
        raise

    ep_evts = EpochEvents(sf=sf)

    list_trial = [None, None, None, None]
    idx_sample = 0
    idx_time = 1
    idx_code = 2
    idx_chan = 3
    if col_sample is not None:
        list_trial[idx_sample] = []
    if col_time is not None:
        list_trial[idx_time] = []
    if col_code is not None:
        list_trial[idx_code] = []
    if col_chan is not None:
        list_trial[idx_chan] = []

    # we read once to determine code and channel types (e.g., int, str ...)
    r = 0
    type_code = 'numeric'
    type_chan = 'numeric'
    while (r < len(evt_list)) and ((type_code ==  'numeric') or (type_chan == 'numeric')):
        line = evt_list[r].split(sep)
        if (type_code == 'numeric') and not (utilsfunc.is_num(line[col_code])):
            type_code = 'string'
        if (type_chan == 'numeric') and not (utilsfunc.is_num(line[col_chan])):
            type_chan = 'string'
        r+=1

    sample_latencies = [None, None, None]
    time_latencies = [None, None, None]

    r = 0
    while r < len(evt_list):
        
        line = evt_list[r].split(sep)
        t = int(line[col_trial_idx])

        if col_sample is not None:
            list_trial[idx_sample] = [int(line[col_sample])]
        if col_time is not None:
            list_trial[idx_time] = [float(line[col_time])]
        if col_code is not None:
            if type_code == 'numeric':
                list_trial[idx_code] = [utilsfunc.try_num(line[col_code])]
            else:
                list_trial[idx_code] = [line[col_code]]
        if col_chan is not None:
            if type_chan == 'numeric':
                list_trial[idx_chan] = [utilsfunc.try_num(line[col_chan])]
            else:
                list_trial[idx_chan] = [line[col_chan]]
                
        if col_tmin_sample is not None:
            sample_latencies[0] = int(line[col_tmin_sample])
        if col_tmin_time is not None:
            time_latencies[0] = float(line[col_tmin_time])
        if col_t0_sample is not None:
            sample_latencies[1] = int(line[col_t0_sample])
        if col_t0_time is not None:
            time_latencies[1] = float(line[col_t0_time])
        if col_tmax_sample is not None:
            sample_latencies[2] = int(line[col_tmax_sample])
        if col_tmax_time is not None:
            time_latencies[2] = float(line[col_tmax_time])

        tmin = latency.Latency(sample=sample_latencies[0], time=time_latencies[0], sf=ep_evts.sf)
        t0 = latency.Latency(sample=sample_latencies[1], time=time_latencies[1], sf=ep_evts.sf)
        tmax = latency.Latency(sample=sample_latencies[2], time=time_latencies[2], sf=ep_evts.sf)
        
        r += 1
        while (r < len(evt_list)) and (t == int(evt_list[r].split(sep)[col_trial_idx])): 
            line = evt_list[r].split(sep)
            t = int(line[col_trial_idx])
            if col_sample is not None:
                # sample must be an integer
                list_trial[idx_sample].append(int(line[col_sample]))
            if col_time is not None:
                # time must be a float
                list_trial[idx_time].append(float(line[col_time]))
            if col_code is not None:
                # code can be numeric/integer or string
                if type_code == 'numeric':
                    list_trial[idx_code].append(utilsfunc.try_num(line[col_code]))
                else:
                    list_trial[idx_code].append(line[col_code])
            if col_chan is not None:
                # chan can be numeric/integer or string
                if type_chan == 'numeric':
                    list_trial[idx_chan].append(utilsfunc.try_num(line[col_chan]))
                else:
                    list_trial[idx_chan].append(line[col_chan])
            r += 1
                           
        evt_trial = Events(sample=list_trial[idx_sample], time=list_trial[idx_time], \
                           code=list_trial[idx_code], chan=list_trial[idx_chan], \
                           sf=ep_evts.sf)
        ep_evts.add_trial(evt_trial, latency_min=tmin, latency0=t0,\
                          latency_max=tmax)

    return ep_evts


##############################################################################
# Class Events and EpochEvents ###############################################
##############################################################################
    
class Events():
    """Events class, storing and manipulating event markers.

    'Events' contains the latency (time and sample), the code and the channel
    of event markers (typically all events of one experiment). Information is
    stored in numpy.ndarrays (Events.lat.sample, Events.lat.time,
    Events.code and Events.chan), in which one given event is stored at the
    same position in all arrays (i.e., information for event 'n' is stored in
    Events.lat.sample[n], Events.lat.sample[n], Events.code[n] and
    Events.chan[n]). For Latency, either time (in seconds) or sample can be
    given. Time/sample, code and chan must be of same length. If sampling frequency
    (sf) is not given, it will be asked when the object is created.

    Parameters
    ----------
    sample : int | list of int | 1D array of int
        Latency in samples of each event marker.
    time : float | list of float | 1D array of float
        Latency in second of each event marker.
    code : int | float | str | list | 1D array
        Code of each event marker.
    chan : int | str | list | 1D array
        Channel of each event marker.
    sf : float
        Sampling frequency of the corresponding data recording.
    """

    def __init__(self, sample=None, time=None, code=None, chan=None, sf=None):
        import numpy as np

        if sf is None:
            sf = input('Enter sampling frequency: ')
        self.sf = float(sf)
        self.lat = latency.Latency(sample=sample, time=time, sf=self.sf)

        if chan is None:
            self.chan = np.array([], dtype=int)
        else: self.chan = np.array(utilsfunc.in_list(chan))

        if code is None:
            self.code = np.array([], dtype=int)
        else: self.code = np.array(utilsfunc.in_list(code))

        if ((self.lat.sample.size) != (self.chan.size)) | \
           ((self.lat.sample.size) != (self.code.size)):
            raise TypeError('sample/time, chan and code must be of same length.')

    def __repr__(self):
        return "class Events, {} events, sf = {} \n latency: {} \n code: {} \n chan: {}".format(self.nb_events(), self.sf, self.lat, self.code, self.chan)

    def get_events(self, idx_evt):
        """Get the events designated by idxEvt and returns them.

        Parameters
        ----------
        idx_evt : int | list of int
            Position(s) of the event(s) to get.

        Returns
        -------
            Events containing only the designated events.
        """
        return Events(sample=self.lat.sample[idx_evt], time=self.lat.time[idx_evt], code=self.code[idx_evt], chan=self.chan[idx_evt], sf=self.sf)

    def del_events(self, idx_evt, print_del_evt=True):
        """Delete the events designated by idxEvt, occurs in place.

        Parameters
        ----------
        idx_evt : int | list of int
            Position(s) of the event(s) to delete.
        print_del_evt : bool
            If True, print the number of deleted events.
        """

        import numpy as np
        idx_evt = utilsfunc.in_list(idx_evt)
        to_print = str(len(idx_evt)) + ' event(s) removed.'
        if print_del_evt is True:
            print(to_print)

        self.lat.del_lat(idx_evt)
        self.code = np.delete(self.code, idx_evt)
        self.chan = np.delete(self.chan, idx_evt)

    def nb_events(self):
        """Return the number of single events.
        """
        return len(self.code)
 
    def sort_events(self):
        """Sort the single events by latency, occurs in place.
        """
        sort_sample = self.lat.sort_sample()
        self.lat.sample = self.lat.sample[sort_sample]
        self.lat.time = self.lat.time[sort_sample]
        self.code = self.code[sort_sample]
        self.chan = self.chan[sort_sample]
        
    def find_events(self, evt=None, sample=None, time=None, code=None, chan=None,\
                    tmin=None, tmax=None, samplemin=None, samplemax=None):
        """Find the specified event(s) and return the position(s).

        Finds the event(s) whose sample, time, chan or code is equal to the
        given value(s) (e.g., Events.find_events(code='onset') will return
        positions of all events whose code is 'onset'). If more than one
        attribute is filled, finds events satisfying both requirements
        (Events.find_events(code='onset', chan=1) will return positions of
        events whose code is 'onset' AND chan is 1). If more than one value
        is given for one attribute, finds events whose attribute is equal to
        either value (Events.find_events(code='onset', chan=[0,1]) will return
        positions of events whose code is 'onset' and chan is 0 OR 1).
        See also Latency.find_lat for sample and time parameters.
        To find event(s) in a restricted time window, use tmin or samplemin
        and tmax or samplemax parameters.

        Parameters
        ----------
        evt : class Events
            If evt is given, finds events with the same Latency, code and chan.
            In this case, other parameters are ignored.
        sample : int | list of  int | 1D array of int
            Sample value(s) to look for.
        time : float | list of float | 1D array of float
            Time value(s) to look for.
        code : int | str | list | 1D array
            Code value(s) to look for.
        chan : int | str | list | 1D array
            Channel value(s) to look for.
        tmin : float
            Only events occurring after time latency tmin are returned.
        tmax : float
            Only events occurring before time latency tmax are returned.
        samplemin : int
            Only events occurring after sample latency samplemin are returned.
        samplemax : int
            Only events occurring before sample latency samplemax are returned.

        Returns
        -------
            Position(s) of the found events.
        """

        import numpy as np
        
        if evt is not None:
            
            if (sample is not None) | (time is not None)\
                | (chan is not None) | (code is not None):
                    raise ValueError ('Either evt OR sample/time/code/chan can be searched.')

#            # first selection on latencies events to corresponding latencies
            idx_select = []
            for e in range(evt.nb_events()):
                sample_index = np.flatnonzero(self.lat.sample == evt.lat.sample[e])
                # keeps only those whose time, code and chan are also equal
                idx_select.extend([s for s in sample_index if (np.abs(self.lat.time[s] - evt.lat.time[e]) < 10**(-10))  \
                                                             & (self.code[s] == evt.code[e]) \
                                                             & (self.chan[s] == evt.chan[e])])
#            idx_select = np.sort(np.asarray(idx_select, dtype=np.int64))

        elif (sample is None) & (time is None) & (code is None) & (chan is None)\
            & (tmin is None) & (tmax is None)\
            & (samplemin is None) & (samplemax is None):
            idx_select = np.flatnonzero(np.zeros(1))
        else:
            select = np.ones(self.nb_events(), dtype=bool)
            if sample is not None:
                select = select & np.isin(self.lat.sample, sample)
            if time is not None:
                select = select & np.isin(self.lat.time, time)

            if tmin is not None:
                select = select & (self.lat.time >= tmin)
            if tmax is not None:
                select = select & (self.lat.time <= tmax)
            if samplemin is not None:
                select = select & (self.lat.sample >= samplemin)
            if samplemax is not None:
                select = select & (self.lat.sample <= samplemax)

            if code is not None:
                select = select & np.isin(self.code, code)
            if chan is not None:
                select = select & np.isin(self.chan, chan)
                
                
            idx_select = np.flatnonzero(select)
            
        # if tmin is not None:
        #     idx_select = idx_select[self.lat.time[idx_select]>=tmin]
        # if tmax is not None:
        #     idx_select = idx_select[self.lat.time[idx_select]<=tmax]

        return np.sort(np.asarray(idx_select, dtype=np.int64))    
    
    
    def add_events(self, evt, sort=True, drop_duplic=False):
        """Add events, occurs in place.

        Adds events to the Events object. If sort is True, events are then
        sorted by latency. If drop_duplic is True, removes duplicated after
        adding events.

        Parameters
        ----------
        evt : class Events
            Contains the event(s) to add.
        sort : bool
            If True, events are sorted by latency after adding the new events.
        drop_duplic : bool
            If True, new events with same time/sample, code and chan are removed
            using drop_duplicates().
        """
        import numpy as np
        self.lat.add_lat(evt.lat)
        self.code = np.concatenate((self.code, evt.code))
        self.chan = np.concatenate((self.chan, evt.chan))
        
        if drop_duplic:
            self.drop_duplicates()
        if sort:
            self.sort_events()

    def find_and_get_events(self, evt=None, sample=None, time=None, code=None, chan=None,\
                            tmin=None, tmax=None, samplemin=None, samplemax=None, print_find_evt=True):
        """Return Events containing only the specified events.

        Use find_events to find designated events and return new Events,
        containing only the selected events.

        Parameters
        ----------
        evt : class obj Events
            If evt is given, selects events with the same Latency, code and chan.
        sample : int | list of int | 1D array of int
            Sample value(s) to select.
        time : float | list of float | 1D array of float
            Time value(s) to select.
        code : int | str | list | 1D array
            Code value(s) to select.
        chan : int | str | list | 1D array
            Channel value(s) to select.
        tmin : float
            Only events occurring after time latency tmin are returned.
        tmax : float
            Only events occurring before time latency tmax are returned.
        samplemin : int
            Only events occurring after sample latency samplemin are returned.
        samplemax : int
            Only events occurring before sample latency samplemax are returned.
        print_find_evt : bool
            If True, print the number of selected events.

        Returns
        -------
            Events containing only the designated events.
        """
        idx_evt = self.find_events(evt=evt, sample=sample, time=time, chan=chan, code=code,\
                                   tmin=tmin, tmax=tmax, samplemin=samplemin, samplemax=samplemax)

        if len(idx_evt) > 0:
            to_print = str(len(idx_evt)) + ' event(s) selected.'
        else:
            to_print = 'Event(s) not found, nothing was selected.'
        if print_find_evt is True:
            print(to_print)
        return self.get_events(idx_evt)
            
    def find_and_del_events(self, evt=None, sample=None, time=None, code=None, chan=None,\
                            tmin=None, tmax=None, samplemin=None, samplemax=None, print_del_evt=True):
        """Remove the specified events, occur in place.

        Use find_events to find designated events and removes them from the
        current Events object.

        Parameters
        ----------
        evt : class Events
            If evt is given, removes events with the same Latency, code and
            chan.
        sample : int | list of int | 1D array of int
            Sample value(s) of events to remove.
        time : float | list of float | 1D array of float
            Time value(s) of events to remove.
        code : int | str | list of int | list of str
            Code value(s) of events to remove.
        chan : int | str | list of int | list of str
            Channel value(s) of events to remove.
        tmin : float
            Only events occurring after time latency tmin are returned.
        tmax : float
            Only events occurring before time latency tmax are returned.
        samplemin : int
            Only events occurring after sample latency samplemin are returned.
        samplemax : int
            Only events occurring before sample latency samplemax are returned.
        print_del_evt : bool
            If True, print the number of deleted events.
        """
        idx_evt = self.find_events(evt=evt, sample=sample, time=time, code=code, chan=chan,\
                                   tmin=tmin, tmax=tmax, samplemin=samplemin, samplemax=samplemax)
        self.del_events(idx_evt, print_del_evt=print_del_evt)

    def copy(self):
        """Return a copy of the current Events.
        """
        import numpy as np
        copy_sample = np.copy(self.lat.sample)
        copy_time = np.copy(self.lat.time)
        copy_code = np.copy(self.code)
        copy_chan = np.copy(self.chan)
        return Events(sample=copy_sample, time=copy_time, code=copy_code, chan=copy_chan, sf=self.sf)

    def to_csv(self, fname, header="sample,time,code,chan", sep=',', save_sample=True, save_time=True, save_code=True, save_chan=True, save_trial_idx=False, trial_idx=None):
        """Export events in fname, csv format.

        Parameters
        ----------
        fname : str
            Name of the file to save.
        header : str
            String for the first line in csv file, should contain column names
            (default "sample,time,code,chan").
        sep : str
            Separator between columns (default ",").
        save_sample : bool
            If True, save the column containing event sample (default True).
        save_time : bool
            If True, save the column containing event time (default True).
        save_code : bool
            If True, save the column containing event code (default True).
        save_chan : bool
            If True, save the column containing event channel (default True).
        save_trial_idx : bool
            If True, save a column containing event trial index. Can be True 
            only for events which have been segmented already (default False).
        trial_idx : list | 1D array
            Contain the trial index for each event, should be provided
            when save_trial_idx is set to True.
        """
        import numpy as np

        idx_col = np.where([save_sample, save_time, save_code, save_chan, save_trial_idx])[0]
        list_col = [self.lat.sample, self.lat.time, self.code, self.chan, trial_idx]

        f = open(fname, 'w')
        f.write(header + '\n')
        for e in range(self.nb_events()):
            evt = [str(list_col[c][e]) for c in idx_col]
            for c in evt[:-1]:
                f.write(c + sep)
            f.write(evt[-1] + '\n')
        f.close()       
        
    def to_txt(self, fname, event_type={}, chan_names={}, header="Type, Description, Position, Length, Channel", sep=','):
        """Export events in fname, text format to be read in BVA.

        Parameters
        ----------
        fname : str
            Name of the file to save.
        event_type : dict
            Specify the type of marker (e.g., 'Stim', 'EMG') for each marker
            code. Type 'Comments' will be assigned to markers with no type specified.
        header : str
            String for the first line in csv file, should contain column names
            (default "Type, Description, Position, Length, Channel").
        sep : str
            Separator between columns (default ",").
        """
        length = [1] * self.nb_events()

        f = open(fname, 'w')
        f.write('Sampling rate: ' + str(int(self.sf)) + 'Hz, SamplingInterval: ' + str(1/self.sf*1000) + 'ms\n')
        f.write(header + '\n')

        for e in range(self.nb_events()):
            if self.code[e] in event_type.keys():
                e_type = event_type[self.code[e]]
            else:
                e_type = 'Comments'
            if self.chan[e] in chan_names.keys():
                chan = chan_names[self.chan[e]]
            else:
                chan = self.chan[e]

            try:
                int(self.code[e])
            except ValueError:
                code = str(self.code[e])
            else:
                code = str(int(self.code[e]))

            f.write(e_type + sep + code + sep + str(int(self.lat.sample[e]))\
                    + sep + str(length[e]) + sep + str(chan) +'\n')
        f.close()

    def to_bva_vmrk(self, fname, event_type={}, chan_names={}):
        """Save file in vmrk format from Brain Vision (format '.vmrk').

        Parameters
        ----------
        fname : str
            Name of the vmrk file to save.
        event_type : dict
            Specify the type of marker (e.g., 'Stim', 'EMG') for each marker
            code. Type 'Comments' will be assigned to markers with no type specified.
        chan_names : dict
            Specify the name of the channel for each channel number in events
            (e.g., chan_names = {-1: 'All'}). Channel numbers are used when no
            channel name is specified.
        """
        import os
        core_name = os.path.split(fname)[-1]
        vmrk_name = fname + '.vmrk'
    #    with codecs.open(vhdrFilename, "w", encoding="utf-8") as f:
    #        muv = u'µ'

        f = open(vmrk_name, 'w')
        f.write('Brain Vision Data Exchange Marker File, Version 2.0\n')
        f.write('; Create from to_bva_vmrk in events.py\n')
        f.write('; The channel numbers are related to the channels in the exported file.')
        f.write('\n')

        f.write('[Common Infos]\n')
        f.write('Codepage=UTF-8\n')
        f.write('DataFile='+core_name+'.eeg\n')
        f.write('\n')

        f.write('[Marker Infos]\n')
        for e in range(self.nb_events()):
            if self.code[e] in event_type.keys():
                e_type = event_type[self.code[e]]
            else:
                e_type = 'Comments'
            if self.chan[e] in chan_names.keys():
                chan = chan_names[self.chan[e]]
            else:
                chan = self.chan[e]

            try:
                int(self.code[e])
            except ValueError:
                code = str(self.code[e])
            else:
                code = str(int(self.code[e]))

            f.write('Mk'+str(e+1)+'='+ e_type +','+code+\
            ','+ str(int(self.lat.sample[e]))+',1,' + str(chan) +'\n')
        f.write('\n')

        f.write('[Marker User Infos]\n')
        f.write('\n')

        f.close()

    def to_bva_markers(self, fname, event_type={}, chan_names={}):
        """Save file in vmrk format from Brain Vision (format '.Markers').

        Parameters
        ----------
        fname : str
            Name of the vmrk file to save.
        event_type : dict
            Specify the type of marker (e.g., 'Stim', 'EMG') for each marker
            code. Type 'Comments' will be assigned to markers with no type specified.
        chan_names : dict
            Specify the name of the channel for each channel number in events
            (e.g., chan_names = {-1: 'All'}). Channel numbers are used when no
            channel name is specified.
        """
        markers_name = fname + '.Markers'

        f = open(markers_name, 'w')
        f.write(('Sampling rate: {}Hz, SamplingInterval: {}ms\n').format(self.sf,1000/self.sf))
        f.write('Type, Description, Position, Length, Channel\n')

        for e in range(self.nb_events()):
            if self.code[e] in event_type.keys():
                e_type = event_type[self.code[e]]
            else:
                e_type = 'Comments'
            if self.chan[e] in chan_names.keys():
                chan = chan_names[self.chan[e]]
            else:
                chan = self.chan[e]

            try:
                int(self.code[e])
            except ValueError:
                code = str(self.code[e])
            else:
                code = str(int(self.code[e]))

#            f.write(eType+', ' + str(e+1)+'='+ eType +','+code+\
#            ','+ str(int(self.lat.sample[e]))+',1,' + str(chan) +'\n')
            f.write(('{}, {}, {}, 1, {}\n').format(e_type,
                                                   code,
                                                   self.lat.sample[e],
                                                   chan))
        f.write('\n')
        f.close()
        
    def get_duplicates(self):
        """Get duplicated events (i.e., same sample/time, code and chan).
        """
        import numpy as np
        print("Checking for duplicates in events...")
        first_evt_idx = np.array([], dtype=int)
        duplicated_evt_idx = np.array([], dtype=int)
        for e in range(self.nb_events()):
            if not (e == duplicated_evt_idx).any():
                evt = self.get_events(e)
                evt_idx = self.find_events(evt=evt)
                if len(evt_idx) > 1:
                    first_evt_idx = np.concatenate((first_evt_idx,[e]*(len(evt_idx)-1)))
                    duplicated_evt_idx = np.concatenate((duplicated_evt_idx,evt_idx[evt_idx!=e]))
                    
        return np.vstack((first_evt_idx,duplicated_evt_idx)).T

    def drop_duplicates(self):
        """Delete duplicated events (i.e., same sample/time, code and chan).
        """
        duplicates = self.get_duplicates()
        self.del_events(duplicates[:,1])            

        
    def segment(self, code_t0=None, pos_events0=None, tmin=0, tmax=1, print_epochs=True):
        """Segment events on the interval [tmin,tmax] around code_t0 events.

        Epoch segmentation: events are segmented on the interval between tmin
        and tmax, around the time latency of the reference (t0) events.
        Reference events are specified either by event code, i.e., events
        whose code is equal to code_t0, or by events positions, i.e., events
        at positions corresponding to pos_events0.
        Events of each segmented epoch are stored in an EpochEvents object
        (class EpochEvents). 

        Parameters
        ----------
        code_t0 : int | str | list
            Code of events to use as reference (t0) events. Does not accept 
            dict_values. 
        pos_events0: int | list
            Position of events to use as reference (t0) events.
        tmin : float
            Start time (in seconds) of the epoch segmentation,
            relative to the reference events (default 0).
        tmax : float
            End time (in seconds) of the epoch segmentation,
            relative to the reference events (default 1s).
        print_epochs : bool
            If True, print the number of epochs (default is True).
        
        Returns
        -------
        ep_evts
            EpochEvents object containing segmented events.
        """
        import numpy as np
        
#        timeSerie = times(tmin, tmax, self.sf)
#        samplemin = timeSerie[0] * self.sf
#        samplemax = timeSerie[-1] * self.sf

        sample_serie = latency.samples(tmin, tmax, self.sf)
        samplemin = sample_serie[0]
        samplemax = sample_serie[-1]

        if pos_events0 is None:
            pos_events0 = []
        else:
            pos_events0 = utilsfunc.in_list(pos_events0)

        if code_t0 is not None:
            pos_events0.extend(self.find_events(code=code_t0))
            
        sample_epochs = self.lat.sample[pos_events0]
        time_epochs = self.lat.time[pos_events0]
#        sampleEpochs.sort()
#        timeEpochs.sort()
        nb_epochs = len(pos_events0)
        if print_epochs is True:
            print('Found {} epoch(s).'.format(nb_epochs))
        
        ep_evts = EpochEvents(sf=self.sf)

        for e in np.arange(nb_epochs):
            idx = np.where((self.lat.sample >= sample_epochs[e] + samplemin) \
                         & (self.lat.sample <= sample_epochs[e] + samplemax))

            evts_trial = Events(sample=self.lat.sample[idx] - (sample_epochs[e] + samplemin), \
                               time=self.lat.time[idx] - time_epochs[e],\
                               chan=self.chan[idx], code=self.code[idx], sf=self.sf)
            ep_evts.add_trial(evts_trial, latency_min=latency.Latency(sample=sample_epochs[e] + samplemin,sf=self.sf),\
                              latency0=latency.Latency(sample=sample_epochs[e], sf=self.sf),\
                              latency_max=latency.Latency(sample=sample_epochs[e] + samplemax, sf=self.sf))

        return ep_evts
    

class EpochEvents():
    """EpochEvents class, storing and manipulating epoch event markers.

    Attributes
    ----------
    list_evts_trials : list
        List of Events objects of consecutive trials (i.e., list_evts_trials[n]
        contains trial n). Latency in single trials' Events is relative to the
        trial's time zero (t0) event.
    tmin : class Latency
        Latency object containing starting time and sample of consecutive trials
        (tmin[n] contains starting latency of trial n).Latencies are given
        relative to the original continous Events object.
    t0 : class Latency
        Latency object containing time and sample of the 'time0' event (i.e.,
        the event used for segmentation) in consecutive trials, relative to the
        original continous Events object.
    tmax : class Latency
        Latency object containing ending time and sample of consecutive trials,
        relative to the original continous Events object.

    Parameters
    ----------
    sf : float
        Sampling frequency of the corresponding data recording.
    """

    def __init__(self, sf=None):

        self.list_evts_trials = []
        if sf is None:
            sf = input('Enter sampling frequency: ')
        self.sf = float(sf)
        self.tmin = latency.Latency(sf=self.sf)
        self.t0 = latency.Latency(sf=self.sf)
        self.tmax = latency.Latency(sf=self.sf)

    def __repr__(self):
        return "class EpochEvents, {} trials, {} events, sf = {} ".format(self.nb_trials(), self.nb_events(), self.sf)

    def add_trial(self, evt_trial, latency_min, latency0, latency_max):
        """Add the events trial.
                
        Parameters
        ----------
        evt_trial : class Events 
            Contains the event(s) to add.
        latency_min : class Latency
            Latency object containing starting time and sample of the trial
            to add, relative to the original continous Events object.
        latency0 : class Latency
            Latency object containing time and sample of the 'time0' event 
            of the trial to add, relative to the original continous Events object.
        latency_max : class Latency
            Latency object containing ending time and sample of the trial
            to add, relative to the original continous Events object.
        """
        self.list_evts_trials.append(evt_trial)
        self.tmin.add_lat(latency_min)
        self.t0.add_lat(latency0)
        self.tmax.add_lat(latency_max)


    def del_trial(self, idx_trial):
        """Delete the events trial.
        """
        idx_trial = utilsfunc.in_list(idx_trial)
        for n, trial in enumerate(idx_trial):
            del self.list_evts_trials[trial-n]
        self.tmin.del_lat(idx_trial)
        self.t0.del_lat(idx_trial)
        self.tmax.del_lat(idx_trial)

    def get_trials(self, idx_trial):
        """Return a new EpochEvents with only specified trials.
        """
        new_evts = EpochEvents(sf=self.sf)
        for trial in utilsfunc.in_list(idx_trial):
            new_evts.add_trial(self.list_evts_trials[trial],\
                               latency_min=latency.Latency(sample=self.tmin.sample[trial], sf=self.sf),\
                               latency0=latency.Latency(self.t0.sample[trial], sf=self.sf),\
                               latency_max=latency.Latency(sample=self.tmax.sample[trial], sf=self.sf))
        return new_evts

    def nb_trials(self):
        """Return the number of trials.
        """
        return len(self.list_evts_trials)

    def nb_events(self):
        """Return the number of single Events.
        """
        e = 0
        for trial in range(self.nb_trials()):
            e += self.list_evts_trials[trial].nb_events()
        return e
        
    def as_continuous(self, drop_duplic=True, sort=True):
        """Return continuous Events.

        Extracts single trials' Events and recreates continuous Events, based
        on tmin Latency: sample latencies in the new continuous events are
        computed by adding sample tmin of each trial to the trial events latencies.

        Parameters
        ----------
        drop_duplic : bool
            If True, searchs and removes events duplicates in the new continuous
            Events (e.g., when one trial Events contained some of the next trial
            events) (default True).
        sort : bool
            If True, returns events sorted by latency.
            
        Returns
        -------
        evts_as_continuous : class Events
            Events object containing continuous events.
        trial_idx : 1D array
            Contains the trial index corresponding to each kept single event.
        """
        import numpy as np
        evts_as_continuous = Events(sf=self.sf)
        trial_idx = np.array([], dtype=int)
        for trial in range(self.nb_trials()):
            evts_as_continuous.add_events(Events(sample=self.list_evts_trials[trial].lat.sample + self.tmin.sample[trial],\
                                                 time=self.list_evts_trials[trial].lat.time + self.t0.time[trial],\
                                                 code=self.list_evts_trials[trial].code,\
                                                 chan=self.list_evts_trials[trial].chan, sf=self.sf), sort=False)
            trial_idx = np.append(trial_idx, ([trial] * self.list_evts_trials[trial].nb_events()))

        if drop_duplic:
            
            duplicates = evts_as_continuous.get_duplicates()
            evts_as_continuous.del_events(duplicates[:,1])
            trial_idx = np.delete(trial_idx, duplicates[:,1])

        if sort:
            sorted_idx = evts_as_continuous.lat.sort_sample()
            trial_idx = trial_idx[sorted_idx]
            evts_as_continuous.sort_events()

        return evts_as_continuous, trial_idx

    def continuous_to_csv(self, fname, header="sample,time,code,chan,trialIdx", sep=',', save_sample=True, save_time=True, save_code=True, save_chan=True, save_trial_idx=True):
        """Export continuous events in fname, csv format.

        Parameters
        -----------
        fname : str
            Name of the file to save.
        header : str
            String for the first line in csv file, should contain column names
            (default "sample,time,code,chan").
        sep : str
            Separator between columns (default ",").
        save_sample : bool
            If True, saves the column containing event sample (default True).
        save_time : bool
            If True, saves the column containing event time (default True).
        save_code : bool
            If True, saves the column containing event code (default True).
        save_chan : bool
            If True, saves the column containing event channel (default True).
        save_trial_idx : bool
            If True, saves a column containing event trial index.
        """
        import numpy as np

        print("Saving as continuous...")
        continuous_evts, trial_idx = self.as_continuous()
        idx_col = np.where([save_sample, save_time, save_code, save_chan, save_trial_idx])[0]
        list_col = [continuous_evts.lat.sample, continuous_evts.lat.time, continuous_evts.code, continuous_evts.chan, trial_idx]

        f = open(fname, 'w')
        f.write(header + '\n')
        for e in range(continuous_evts.nb_events()):
            evt = [str(utilsfunc.try_int(list_col[c][e])) for c in idx_col]
            for c in evt[:-1]:
                f.write(c + sep)
            f.write(evt[-1] + '\n')
        f.close()
       
    def to_csv(self, fname, header=["sample","time","code","chan","trial_idx","trial_raw_tmin.sample","trial_raw_tmin.time","trial_raw_t0.sample","trial_raw_t0.time","trial_raw_tmax.sample","trial_raw_tmax.time"],\
               sep=',', save_sample=True, save_time=True, save_code=True, save_chan=True, save_trial_idx=True, save_tmin=True, save_t0=True, save_tmax=True):
        """Export segmented events in fname, csv format.
        
        Parameters
        ----------
        fname : str
            Name of the file to save.
        header : list
            List of head columns to insert as first line in csv file, should 
            contain column names (default ["sample","time","code","chan",
            "trial_idx","trial_raw_tmin.sample","trial_raw_tmin.time",
            "trial_raw_t0.sample","trial_raw_t0.time","trial_raw_tmax.sample",
            "trial_raw_tmax.time"]).
        sep : str
            Separator between columns (default ",").
        save_sample : bool
            If True, saves the column containing event sample (default True).
        save_time : bool
            If True, saves the column containing event time (default True).
        save_code : bool
            If True, saves the column containing event code (default True).
        save_chan : bool
            If True, saves the column containing event channel (default True).
        save_trial_idx : bool
            If True, saves a column containing event trial index (default True).
        save_tmin : bool
            If True, saves the columns containing tmin samples and tmin time
            (default True).
        save_t0 : bool
            If True, saves the columns containing t0 samples and t0 time
            (default True).
        save_tmax : bool
            If True, saves the columns containing tmax samples and tmax time
            (default True).
        """

        import numpy as np

        print("Saving as segmented...")
        idx_evt_col = np.where([save_sample, save_time, save_code, save_chan])[0]
        idx_info_col = np.where([save_trial_idx, save_tmin, save_tmin, save_t0, save_t0, save_tmax, save_tmax])[0]

        f = open(fname, 'w')
        f.write(sep.join(header) + '\n')

        for t in range(self.nb_trials()):
            evt_col = [self.list_evts_trials[t].lat.sample, self.list_evts_trials[t].lat.time, self.list_evts_trials[t].code, self.list_evts_trials[t].chan]
            info_col = [t, self.tmin.sample[t], self.tmin.time[t], self.t0.sample[t], self.t0.time[t], self.tmax.sample[t], self.tmax.time[t]]

            for e in range(self.list_evts_trials[t].nb_events()):
                evt = [str(evt_col[c][e]) for c in idx_evt_col] + [str(info_col[c]) for c in idx_info_col]
                for c in evt[:-1]: f.write(c + sep)
                f.write(evt[-1] + '\n')
        f.close()
    
    def get_data(self, data, drop_trials = []):
        """Get data segments corresponding to EpochEvents.
    
        Parameters
        ----------
        data : 2D array
            Contains continuous data (axis 0: channels, axis 1: time).
        drop_trials : list | 1D array
            Indices of trials that will not be included in data epochs.
    
        Returns
        -------
        epochs: 3D array
            Contains data segments (axis 0: trials, axis 1: channels, axis 2: time).
        """
        import numpy as np
    
        if data.ndim == 1:
            print('Warning, data is 1D array and must be transposed! Ignore me if your data contains only one channel.')
            data = data[np.newaxis]
			
        drop_trials = utilsfunc.in_list(drop_trials)
        trials = np.arange(self.nb_trials())
        for trial in drop_trials:
            if trial not in trials:
                raise IndexError('drop_trials ' + str(trial) + ': out of bound.')
        trials = np.delete(trials, drop_trials)
    
        if (self.tmin.sample[trials] < 0).any():
            raise ValueError('All tmin.sample must be positive, use drop_trials if necessary.')
        elif (self.tmax.sample[trials] > data.shape[1]).any():
            raise ValueError('All tmax.sample must be contained in data, use drop_trials if necessary.')
    
        length_epoch = self.tmax.sample[0] - self.tmin.sample[0] + 1
        epochs = np.empty((trials.shape[0], data.shape[0], length_epoch))
        for idx, trial in enumerate(trials):
            epochs[idx] = data[:, self.tmin.sample[trial] : self.tmax.sample[trial] + 1]
        return epochs
    
