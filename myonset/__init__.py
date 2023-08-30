"""
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

from .emgtools import (set_log_file, tkeo, filtfilter, hpfilter, lpfilter, notch_filter, 
                       moving_avg, integrated_profile, 
                       get_onset_ip, 
                       global_var, detector_var, detector_dbl_th, 
                       signal_windows, get_onsets, get_onsets_dbl_th, 
                       get_signal_portions, get_signal_max, somf, get_onset_somf, show_trial)

from .events import (Events, EpochEvents, load_continuous, load_segmented)
                   
from .latency import times, find_times   

from .utils import use_mne, use_txt
from .viz.viz_emg import VizApplication as Viz
