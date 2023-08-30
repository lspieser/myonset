# -*- coding: utf-8 -*-
"""
Created on Mon Jul 21 17:23:41 2014

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

import sys
from PyQt5 import QtGui, QtCore, QtWidgets
#from PyQt5.QtWidgets import QApplication, QWidget , QTabWidget
import pyqtgraph as pg
import numpy as np
# from ..events import Events
# from ..latency import Latency
from myonset import Events
from myonset.latency import Latency, times, find_times
from copy import deepcopy


## Always start by initializing Qt (only once per application)

class CustomEventPlot(pg.PlotItem):
    
    def __init__(self, movable_1, movable_2, sf=None, color_events=['y','b',pg.mkPen(color=(0, 201, 255, 255)),'r']):
        super(CustomEventPlot,self).__init__()
        self.enableAutoRange = False
        self.label = pg.LabelItem(justify='right')
        self.movable_1 = movable_1
        self.movable_2 = movable_2
        self.color_events = color_events
        self.list_plot_lines = []
 
    # def new_events_epoch(self, events_epoch):
    #     self.list_plot_lines = []
    #     for e in range(len(events_epoch.code)):

    #         if events_epoch.code[e] == self.movable_1:
    #             line = self.addLine( x=events_epoch.lat.time[e], movable=True, pen=self.color_events[1])
    #             line.code = events_epoch.code[e]
    #             self.list_plot_lines.append(line)

    #         elif events_epoch.code[e] == self.movable_2:
    #             line = self.addLine( x=events_epoch.lat.time[e], movable=True, pen=self.color_events[2])
    #             line.code = events_epoch.code[e]
    #             self.list_plot_lines.append(line)

    #         else:
    #             line = self.addLine( x=events_epoch.lat.time[e], movable=False, pen=self.color_events[0])
    #             line.code = events_epoch.code[e]
    #             self.list_plot_lines.append(line)    
                

    def new_events_epoch(self, movable_events, fix_events):
        self.list_plot_lines = []
        for e in range(movable_events.nb_events()):

            if movable_events.code[e] == self.movable_1:
                line = self.addLine( x=movable_events.lat.time[e], movable=True, pen=self.color_events[1])
                line.code = movable_events.code[e]
                self.list_plot_lines.append(line)

            elif movable_events.code[e] == self.movable_2:
                line = self.addLine( x=movable_events.lat.time[e], movable=True, pen=self.color_events[2])
                line.code = movable_events.code[e]
                self.list_plot_lines.append(line)

        for e in range(fix_events.nb_events()):
            line = self.addLine( x=fix_events.lat.time[e], movable=False, pen=self.color_events[0])
            line.code = fix_events.code[e]
            self.list_plot_lines.append(line) 


#    def onClick(self,eventMouse,eventKey):
    def on_click(self,event_mouse):    
        
        vb = self.vb
        modifiers = QtWidgets.QApplication.keyboardModifiers()
      
#        if event_mouse.double() : print('double click')
#        else: print('not double')
        
        if ( (event_mouse.button() == QtCore.Qt.LeftButton) ):#& (eventKey.key() == QtCore.Qt.Key_Control) ):
#            event_mouse.accept()
            if modifiers == QtCore.Qt.ControlModifier:
                click_pos = vb.mapToView(event_mouse.lastPos())
                self.add_event(click_pos, self.movable_1, movable=True, line_color=self.color_events[1])
            else:
                self.mousePressEvent(event_mouse)
        elif ( (event_mouse.button() == QtCore.Qt.RightButton) ):#& (eventKey.key() == QtCore.Qt.Key_Control) ):
#            event_mouse.accept()
            if modifiers == QtCore.Qt.ControlModifier:
                click_pos = vb.mapToView(event_mouse.lastPos())
                self.add_event(click_pos, self.movable_2, movable=True, line_color=self.color_events[2])
            else:
                line_under_mouse = [ line for line in self.list_plot_lines if (line.movable) & (line.isUnderMouse())]
                if len(line_under_mouse) > 0:
                    self.remove_event(line_under_mouse[0])
                else:
                    self.mousePressEvent(event_mouse)
        else:
            self.mousePressEvent(event_mouse)

            
    def add_event(self, pos, code, movable=False, line_color='y'):
        line = self.addLine(x=pos, movable=movable, pen=line_color)
        line.code = code
        self.list_plot_lines.append(line)

    def remove_event(self, line):
        self.removeItem(line)
        self.list_plot_lines.remove(line)

    def get_events_pos(self,idx):
        if type(idx) is int : idx = [idx]     
        return np.array([self.list_plot_lines[n].pos()[0] for n in idx])

    def get_events_code(self,idx):
        if type(idx) is int : idx = [idx]     
        return np.array([self.list_plot_lines[n].code for n in idx])

#    def setKeyboardPrevNext(self,listKeys):
#        self.keyGoToPrev = listKeys[0]        
#        self.keyGoToNext = listKeys[1]
#        
#    def pressKey(self, eventKey):
#         key = eventKey.key()
#         print(key)
##         eventKey.accept()
#         if key == QtCore.Qt.Key_Space:
#            print('space')


class VizUi(QtWidgets.QWidget):
    
    def __init__(self, write_evt_file=True, fname_evts='viz_events.csv'):
        super(VizUi,self).__init__()
        
        self.nb_epoch = 0
        self.nb_chan = 0
        self.tmin_plot = ''
        self.tmax_plot = ''
        self.vmin_plot = ''
        self.vmax_plot = ''
        self.chan_scale = range(self.nb_chan)
        
        global current_epoch 
        current_epoch = ''

        if write_evt_file:
            self.fname_evts = fname_evts
        
        self.initUi()
        self.set_keyboard_prev_next()
        self.key_delete_movable = QtCore.Qt.Key_D
        self.keyPressEvent = self.press_key


#    def keyPressEvent(self, eventKey):
#         key = eventKey.key()
#         print(key)

    def closeEvent(self, event):
        self.save_events()
        print('Closing...')
        event.accept()
        
    def get_events(self):
        self.update_movable_events()
        all_events = self.fix_events.copy()
        all_events.add_events(self.movable_events)
        self.plot_epoch()
        return all_events

    def get_epoch_events(self, idx=None):
        self.update_movable_events()
        all_events = self.fix_events.copy()
        all_events.add_events(self.movable_events)
        self.plot_epoch()
        if idx is None:
            return all_events.segment(self.code_t0, tmin=self.tmin_plot, tmax=self.tmax_plot)
        else:
            return all_events.segment(self.code_t0, tmin=self.tmin_plot, tmax=self.tmax_plot).get_trials(idx)
			
        
    def save_events(self):
        all_events = self.get_events()
        all_events.to_csv(self.fname_evts)
        print(('Saving events in {}...').format(self.fname_evts))
        
    def press_key(self, eventKey):
         key = eventKey.key()
#         print(key)
         if key == self.key_go_to_prev: self.go_to_prev()
         elif key == self.key_go_to_next: self.go_to_next()
         elif key == self.key_delete_movable: self.delete_movable()
#         else: self.keyPressEvent()
         
    def load_data(self, data, events, code_t0, tmin=-.5, tmax=1.5, channels='all', code_movable_1='onset', code_movable_2='offset', sync_chan=[[0,1],[0,1],[2,3],[2,3]], group_chan=True, list_trials=None, random_order=False):
        # self.t = times 
        # self.t0sample =  np.abs(0 - self.t).argmin()
        # self.tmin_plot = self.t[0]
        # self.tmax_plot = self.t[-1]
        # self.data = data_epochs
        # self.nb_epoch = data_epochs.shape[0]
        # if self.nb_epoch == 0:
        #     raise ValueError('No trial found in data!')
        
        movable_events_idx = events.find_events(code=[code_movable_1,code_movable_2])
        self.movable_events = events.get_events(movable_events_idx)
        self.fix_events = events.copy()
        self.fix_events.del_events(movable_events_idx, print_del_evt=False)
        
        self.data = data
        
        self.code_t0 = code_t0
        self.sf = events.sf
        self.tmin_plot = tmin
        self.tmax_plot = tmax
        self.set_time_data()
        
        self.nb_epoch = self.ep_events.nb_trials()
        if  self.nb_epoch == 0:
            raise ValueError('No trial found!')
       
        if list_trials is None:
            self.list_epochs = np.arange(self.nb_epoch)
        else: 
            self.list_epochs = np.asarray(list_trials)
            
        # if random_order is True:
        #     self.list_epochs = np.random.permutation(self.list_epochs)
        #     self.user_info_epoch = np.arange(self.nb_epoch)
        # else:
        #     self.user_info_epoch = self.list_epochs
            
        if (self.list_epochs >= self.nb_epoch).any():
            raise ValueError(('Data contains only {} trials, can not plot trials {} .').format(self.nb_epoch, self.list_epochs[self.list_epochs >= self.nb_epoch]))
        self.nb_epoch = len(self.list_epochs)

        if random_order is True:
            self.list_epochs = np.random.permutation(self.list_epochs)
            self.user_info_epoch = np.arange(self.nb_epoch)
        else:
            self.user_info_epoch = self.list_epochs
            
            
        if channels == 'all': 
            self.nb_chan = self.data_epochs.shape[1]
            self.channels = range(self.nb_chan)
        else: 
            self.channels = [chan for chan in channels if chan < self.data_epochs.shape[1]]
            self.nb_chan = len(self.channels)
            
        self.sync_chan = []
        for chan in self.channels:
            if len(sync_chan) > chan:
                self.sync_chan.append([c for c in sync_chan[chan] if c in self.channels])
            else:
                self.sync_chan.append([chan])
#        else:
#            raise IndexError('sync_chan parameter must contain information for all displayed channels, channels {} are missing.'.format([_ for _ in self.channels if _ >= len(sync_chan)]) )

        for c in self.sync_chan : 
            if any(np.abs(np.diff(c)) > 1 ) & (group_chan): 
                print('Warning: Can not group non contiguous channels, group channels set to False')
                group_chan = False
        if group_chan :
            self.group_chan = [] 
            for group in self.sync_chan: 
                if group not in self.group_chan: self.group_chan.append(group) 
        else: self.group_chan = [range(self.nb_chan)]

        self.vmin_plot = [] 
        self.vmax_plot = [] 
        for c in range(self.nb_chan):
#            self.vmin_plot.append(self.data[:,self.sync_chan[c],:].min()*1.1)
#            self.vmax_plot.append(self.data[:,self.sync_chan[c],:].max()*1.1)        
            self.vmin_plot.append(self.data_epochs[:,self.sync_chan[c],:].min() - np.abs(self.data_epochs[:,self.sync_chan[c],:].min()*.01))
            self.vmax_plot.append(self.data_epochs[:,self.sync_chan[c],:].max() + np.abs(self.data_epochs[:,self.sync_chan[c],:].max()*.01))        

        self.movable_1 = code_movable_1
        self.movable_2 = code_movable_2
        
        # Makes sure no movable event is attached to more than one channel
        if any(self.movable_events.find_events(chan=-1)):
            raise ValueError("Events {}: only events linked to one channel can be movable, please link each {} and {} to only one channel.".format(self.movable_events.find_events(chan=-1), self.movable_1,self.movable_2))
        
        global current_epoch 
        current_epoch = 0

        self.event_plot = []
        self.vb = []
        for group in self.group_chan:
            group_graph = pg.GraphicsLayoutWidget()
            for c in group:
                self.event_plot.append(CustomEventPlot(self.movable_1, self.movable_2))
                self.vb.append(self.event_plot[-1].vb)
                self.vb[-1].mousePressEvent = self.event_plot[-1].on_click
#                self.vb[-1].mouseDoubleClickEvent = self.event_plot[-1].onDoubleClick
    #            self.vb[-1].keyPressEvent = self.event_plot[-1].pressKey

                self.event_plot[-1].setXLink(self.event_plot[0])
                self.event_plot[-1].setYLink(self.event_plot[self.channels.index(self.sync_chan[self.channels.index(c)][0])])
    
                group_graph.addItem(self.event_plot[-1])
                group_graph.nextRow()
            self.win.addWidget(group_graph)
#            self.win.nextRow()
            
#            self.event_plot[c].getViewBox().setLimits(yMin = self.data[:,self.sync_chan[c],:].min()*1.1, yMax = self.data[:,self.sync_chan[c],:].max()*1.1)
           
#            if c > 0: 
#                self.event_plot[c].setXLink(self.event_plot[0])
#                self.event_plot[c].setYLink(self.event_plot[self.sync_chan[c][0]])
        
        self.plot_epoch()
        # self.slider.setMinimum(0)
        # self.slider.setMaximum(self.nb_epoch-1)
        self.slider.setMinimum(np.min(self.user_info_epoch))
        self.slider.setMaximum(np.max(self.user_info_epoch))
        self.combo_chan_scale.clear()
        self.combo_chan_scale.addItems(['all channels'] + [ str(c) for c in range(self.nb_chan)])

    def set_time_data(self):
        self.t = times(self.tmin_plot, self.tmax_plot, self.sf)
        self.t0sample = find_times(self.t,0)
        self.ep_events = self.fix_events.segment(code_t0=self.code_t0, tmin=self.tmin_plot, tmax=self.tmax_plot, print_epochs=False)
        self.data_epochs = self.ep_events.get_data(self.data)
        for c in range(self.nb_chan):
            self.event_plot[c].getViewBox().setXRange(self.tmin_plot,self.tmax_plot,padding=0)

    def data_plot(self):
        global current_epoch
        for c in range(self.nb_chan):
            self.event_plot[c].plot(x=self.t, y=self.data_epochs[self.list_epochs[current_epoch],self.channels[c],:])
            self.event_plot[c].getViewBox().setYRange(self.vmin_plot[c],self.vmax_plot[c],padding=0)
            self.event_plot[c].getViewBox().setXRange(self.tmin_plot,self.tmax_plot,padding=0)
        
    def plot_epoch(self):
        global current_epoch
        for c in range(self.nb_chan):
            fix_chan_events = self.ep_events.list_evts_trials[self.list_epochs[current_epoch]].find_and_get_events(chan=[-1, self.channels[c]], print_find_evt=False)

            movable_epoch_idx = self.movable_events.find_events(chan=self.channels[c], tmin=self.ep_events.tmin.time[self.list_epochs[current_epoch]], tmax=self.ep_events.tmax.time[self.list_epochs[current_epoch]])
            movable_chan = self.movable_events.get_events(movable_epoch_idx)
            movable_chan.lat = Latency(sample=movable_chan.lat.sample - self.ep_events.tmin.sample[self.list_epochs[current_epoch]],\
                                       time=movable_chan.lat.time - self.ep_events.tmin.time[self.list_epochs[current_epoch]] + self.tmin_plot,\
                                       sf=self.sf)
            self.movable_events.del_events(movable_epoch_idx, print_del_evt=False) # remove it before user change anything

            self.event_plot[c].clear()
            self.event_plot[c].new_events_epoch(movable_chan, fix_chan_events)
        self.data_plot()
        self.box_go_to.setText(str(self.user_info_epoch[current_epoch]))
        self.slider.setValue(self.user_info_epoch[current_epoch])

    def get_plot_events(self, chan, movable_events=None, data_time_range=True):
        if movable_events is True: selected_lines = [ li[0] for li in enumerate(self.event_plot[chan].list_plot_lines) if (li[1].movable)]
        elif movable_events is False: selected_lines = [ li[0] for li in enumerate(self.event_plot[chan].list_plot_lines) if (li[1].movable is False)]
        else: selected_lines = range(len(self.event_plot[chan].list_plot_lines))
        if data_time_range is True : selected_lines = [ li for li in selected_lines if self.t[0] <= self.event_plot[chan].get_events_pos(li) <= self.t[-1]]
        
        # create latencies to enter time and sample separately below
        evt_lat = Latency(time=self.event_plot[chan].get_events_pos(selected_lines), sf=self.sf)        
        return Events(time=evt_lat.time, sample=evt_lat.sample + self.t0sample, chan=[self.channels[chan]]*len(selected_lines), code=self.event_plot[chan].get_events_code(selected_lines), sf=self.sf)
#        return Events(time = self.event_plot[chan].getEventsPos(selectedLines), chan = [self.channels[chan]] * len(selectedLines), code = self.event_plot[chan].getEventsCode(selectedLines), sf = self.sf)
    
    def update_movable_events(self):
        global current_epoch
        for c in range(self.nb_chan):
            plot_events = self.get_plot_events(c, movable_events=True, data_time_range=True)
            plot_events.lat = Latency(sample=plot_events.lat.sample + self.ep_events.tmin.sample[self.list_epochs[current_epoch]],\
                                      time=plot_events.lat.time + self.ep_events.tmin.time[self.list_epochs[current_epoch]] - self.tmin_plot,\
                                      sf=self.sf)
            self.movable_events.add_events(plot_events)
        # if self.write_evt_file : self.save_events()
               
    def go_to_prev(self):
        global current_epoch
        self.update_movable_events()
        if current_epoch >0:
            current_epoch-=1
        self.plot_epoch()
            
    def go_to_next(self):
        global current_epoch
        self.update_movable_events()
        if current_epoch + 1 < self.nb_epoch:
            current_epoch+=1
        self.plot_epoch()

    def go_to_box(self):
        global current_epoch
        self.update_movable_events()
        try:
            new_epoch = int(self.box_go_to.text())
        except ValueError: 
#            print('Enter a valid epoch number (type: integer)')
#            self.boxGoTo.setText('Only integer type')
            pass
        # if 0 <= new_epoch < self.nb_epoch:
        if new_epoch in self.user_info_epoch:
            current_epoch = np.where(self.user_info_epoch == new_epoch)[0][0]
        self.plot_epoch()
 
    def go_to_slider(self):
        global current_epoch
        if self.user_info_epoch[current_epoch] != self.slider.value(): #does everything only if change was made through slider (otherwise it is already done)
            self.update_movable_events()
            try: 
                current_epoch = np.where(self.user_info_epoch == self.slider.value())[0][0]
            except IndexError:
                pass
            self.plot_epoch()

    def set_time_box(self):
        self.update_movable_events()
        try:
            self.tmin_plot = float(self.box_show_from.text())
        except ValueError: 
            pass
        try:
            self.tmax_plot = float(self.box_show_until.text())
        except ValueError: 
            pass
        self.set_time_data()
        self.plot_epoch()
        # for c in range(self.nb_chan):
            # self.event_plot[c].getViewBox().setXRange(self.tmin_plot,self.tmax_plot,padding=0)
    
    def set_chan_scale(self):
        try: self.chan_scale = self.sync_chan[int(self.combo_chan_scale.currentText())]
        except: self.chan_scale = range(self.nb_chan)
        self.set_vertical_scale()
            
    def set_vertical_scale(self):
        try: 
            for c in self.chan_scale: self.vmin_plot[c] = float(self.box_vmin.text())
        except: pass
        try: 
            for c in self.chan_scale: self.vmax_plot[c] = float(self.box_vmax.text())
        except: pass

        for c in self.chan_scale:
            self.event_plot[c].getViewBox().setYRange(self.vmin_plot[c],self.vmax_plot[c],padding=0)
            
    def reset_scale(self):
        for c in range(self.nb_chan):
#            self.vmin_plot[c] = self.data[:,self.sync_chan[c],:].min()*1.1
#            self.vmax_plot[c] = self.data[:,self.sync_chan[c],:].max()*1.1        
            self.vmin_plot[c] = self.data[:,self.sync_chan[c],:].min() - np.abs(self.data[:,self.sync_chan[c],:].min()*.01)
            self.vmax_plot[c] = self.data[:,self.sync_chan[c],:].max() + np.abs(self.data[:,self.sync_chan[c],:].max()*.01)   

            self.event_plot[c].getViewBox().setYRange(self.vmin_plot[c],self.vmax_plot[c],padding=0)
        self.box_vmin.clear()
        self.box_vmax.clear()
        self.combo_chan_scale.setCurrentIndex(0)

    def set_keyboard_prev_next(self):        
        key_idx = self.combo_prev_next.currentIndex()
        if key_idx == 0 : 
            self.key_go_to_prev = QtCore.Qt.Key_Alt
            self.key_go_to_next = QtCore.Qt.Key_Space
        elif key_idx == 1 : 
            self.key_go_to_prev = QtCore.Qt.Key_Left
            self.key_go_to_next = QtCore.Qt.Key_Right
        elif key_idx == 2 : 
            self.key_go_to_prev = QtCore.Qt.Key_A
            self.key_go_to_next = QtCore.Qt.Key_Z
        elif key_idx == 3 : 
            self.key_go_to_prev = QtCore.Qt.Key_Q
            self.key_go_to_next = QtCore.Qt.Key_W
    
    def delete_movable(self):
        global current_epoch
        for c in range(self.nb_chan):
            movable_lines = [ line for line in self.event_plot[c].list_plot_lines if line.movable ]
            for line in movable_lines: self.event_plot[c].remove_event(line)

    # def reset_movable(self):
    #     global current_epoch
    #     self.delete_movable()
    #     for c in range(self.nb_chan):
    #         chan_events = self.events.list_evts_trials[self.list_epochs[current_epoch]].find_and_get_events(chan=[self.channels[c]], print_find_evt=False)
    #         self.event_plot[c].new_events_epoch(chan_events)        
        
    def initUi(self):
        ## Define a top-level widget to hold everything
        global current_epoch        
#        self.w = QtGui.QWidget()

        ## Create some widgets to be placed inside
        tab_widget = QtWidgets.QTabWidget()
        
        navigation_widget = QtWidgets.QWidget()
        navigation_layout = QtWidgets.QGridLayout()
        self.btn_back = QtWidgets.QPushButton('<<')
        self.btn_back.clicked.connect(self.go_to_prev)
        self.btn_fwd = QtWidgets.QPushButton('>>')
        self.btn_fwd.clicked.connect(self.go_to_next)

        label_current = QtWidgets.QLabel('Epoch ', alignment = QtCore.Qt.AlignCenter)
        self.box_go_to = QtWidgets.QLineEdit(str(current_epoch))
        self.box_go_to.returnPressed.connect(self.go_to_box)
        
        self.slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.slider.valueChanged.connect(self.go_to_slider)

        self.btn_delete_mrk = QtWidgets.QPushButton('Delete epoch markers (d)')
        self.btn_delete_mrk.clicked.connect(self.delete_movable)
        self.btn_save_events = QtWidgets.QPushButton('Save events')
        self.btn_save_events.clicked.connect(self.save_events)
        # self.btn_reset_mrk = QtWidgets.QPushButton('Reset markers')
        # self.btn_reset_mrk.clicked.connect(self.reset_movable)
        
        navigation_layout.addWidget(self.btn_back, 1, 0, 1, 3)
        navigation_layout.addWidget(label_current, 1, 3, 1, 1)   # label goes in down-middle
        navigation_layout.addWidget(self.box_go_to, 1, 4, 1 , 1)   # text box goes in down-middle
        navigation_layout.addWidget(self.btn_fwd, 1, 5, 1, 3)   # button goes in down-right
        # navigation_layout.addWidget(self.btn_delete_mrk, 2, 0, 1, 4)   # button goes in down-right
        # navigation_layout.addWidget(self.btn_reset_mrk, 2, 4, 1, 4)   # button goes in down-right
        navigation_layout.addWidget(self.slider, 2, 0, 1, 8)   # button goes in down-right
        navigation_layout.addWidget(self.btn_delete_mrk, 3, 0, 1, 1)   # button goes in down-right
        navigation_layout.addWidget(self.btn_save_events, 3, 3, 1, 5)   # button goes in down-right

        navigation_layout.setColumnStretch(0,1)
        navigation_layout.setColumnStretch(1,1)
        navigation_layout.setColumnStretch(2,1)
        navigation_layout.setColumnStretch(3,1)
        navigation_layout.setColumnStretch(4,1)
        navigation_layout.setColumnStretch(5,1)
        navigation_layout.setColumnStretch(6,1)
        navigation_layout.setColumnStretch(7,1)
        
        navigation_widget.setLayout(navigation_layout)
        tab_widget.addTab(navigation_widget,'Navig.')
                   
#        config_widget = QtGui.QWidget()
        config_widget = QtWidgets.QWidget()
        config_layout = QtWidgets.QGridLayout()
        
        label_time_range= QtWidgets.QLabel('Set new time range:', alignment = QtCore.Qt.AlignCenter)
        self.box_show_from = QtWidgets.QLineEdit(self.tmin_plot)
        self.box_show_from.setPlaceholderText('Xmin')
        self.box_show_from.returnPressed.connect(self.set_time_box)
        self.box_show_until = QtWidgets.QLineEdit(self.tmax_plot)
        self.box_show_until.setPlaceholderText('Xmax')
        self.box_show_until.returnPressed.connect(self.set_time_box)

        label_vertical_scale = QtWidgets.QLabel('Scale range:', alignment = QtCore.Qt.AlignCenter)
        self.combo_chan_scale = QtWidgets.QComboBox()
        self.combo_chan_scale.addItems(['all channels'] + [ str(c) for c in range(self.nb_chan)])
        self.combo_chan_scale.currentIndexChanged.connect(self.set_chan_scale)
        self.box_vmin = QtWidgets.QLineEdit()
        self.box_vmin.setPlaceholderText('Ymin')
        self.box_vmin .returnPressed.connect(self.set_vertical_scale)
        self.box_vmax = QtWidgets.QLineEdit()
        self.box_vmax.setPlaceholderText('Ymax')
        self.box_vmax .returnPressed.connect(self.set_vertical_scale)
        self.btn_reset_scale = QtWidgets.QPushButton('Reset scale')
        self.btn_reset_scale.clicked.connect(self.reset_scale)


        label_prev_next= QtWidgets.QLabel('Go to Prev / Next:', alignment = QtCore.Qt.AlignCenter)
        self.combo_prev_next = QtWidgets.QComboBox()
        self.combo_prev_next.addItems(['Alt / space bar'] + [u'\u2190 / \u2192'] + ['A / Z'] + ['Q / W'])
        self.combo_prev_next.currentIndexChanged.connect(self.set_keyboard_prev_next)

        config_layout.addWidget(label_time_range, 0, 0, 1, 1)   # button goes in down-right
        config_layout.addWidget(self.box_show_from, 0, 1, 1, 1)   # button goes in down-right
        config_layout.addWidget(self.box_show_until, 0, 2, 1, 1)   # button goes in down-right

        config_layout.addWidget(label_vertical_scale, 0, 3, 1, 1)   # button goes in down-right
        config_layout.addWidget(self.combo_chan_scale, 0, 4, 1, 1)   # button goes in down-right
        config_layout.addWidget(self.box_vmin, 0, 5, 1, 1)   # button goes in down-right
        config_layout.addWidget(self.box_vmax, 0, 6, 1, 1)   # button goes in down-right
        config_layout.addWidget(self.btn_reset_scale, 0, 7, 1, 1)   # button goes in down-right

        config_layout.addWidget(label_prev_next, 1, 0, 1, 1)   # button goes in down-right
        config_layout.addWidget(self.combo_prev_next, 1, 1, 1, 1)   # button goes in down-right

        config_widget.setLayout(config_layout)
        tab_widget.addTab(config_widget,'Config.')

        self.listw = QtWidgets.QListWidget()
        
        self.win = QtWidgets.QSplitter(QtCore.Qt.Vertical)
#        for group in self.group_chan:
#            self.win.addWidget(pg.GraphicsLayoutWidget)
        pg.setConfigOptions(antialias=True)
        
        ## Create a grid layout to manage the widgets size and position
        layout = QtWidgets.QHBoxLayout()
        v_splitter = QtWidgets.QSplitter(QtCore.Qt.Vertical)
        
        ## Add widgets to the layout in their proper positions
#        layout.addWidget(self.win,0,0,1,4)  # plot goes on right side, spanning 4 rows
#        layout.addWidget(tabWidget,1,0,4,4)   # button goes in down-left
        v_splitter.addWidget(self.win)  # plot goes on right side, spanning 4 rows
        v_splitter.addWidget(tab_widget)   # button goes in down-left

        layout.addWidget(v_splitter)
#        self.w.setLayout(layout)
        self.setLayout(layout)




class VizApplication(QtWidgets.QApplication):
    
    def __init__(self,args):
        app = QtCore.QCoreApplication.instance()
        if app is None:
#        app = QApplication(sys.argv) 
            QtWidgets.QApplication.__init__(self,args)
        self.window = VizUi()
        
    def load_data(self, data, events, code_t0, tmin=-.5, tmax=1.5, channels='all', code_movable_1='onset', code_movable_2='offset', sync_chan=[[0,1],[0,1],[2,3],[2,3]], group_chan=True, list_trials=None, random_order=False):
        """Load data and sets viz window view.
    
        Parameters
        ----------
        data : 2D array
            Data array, dimensions should be channels x time.
        events : Events object
            Events corresponding to data.
        code_t0 : list | 1D array
            Event code(s) to use in events to define trials (e.g., stimulus code 
            used for segmentation).
        tmin : float
            Minimum time to plot, relative to code_t0 event. To change tmin after 
            plotting, use "Set new time range" in Configuration panel (default -0.5s).
        tmax : float
            Maximum time to plot, relative to code_t0 event. To change tmax after 
            plotting, use "Set new time range" in Configuration panel (default 1.5s).
        channels : list of int
            List of channel indices to represent, if equal to 'all', all channels
            of data are used (default is 'all').
        code_movable_1 : int | str | float
            Code of events with which the user can interact. All events whose code
            is equal to 'code_movable_1' are displayed in dark blue and can be 
            moved (left click + drag), deleted (right click), or inserted 
            (Ctrl + left click) (default is 'onset').
        code_movable_2 : int | str | float
            Code of events with which the user can interact. All events whose code
            is equal to 'code_movable_2' are displayed in light blue and can be 
            moved (left click + drag), deleted (right click), or inserted 
            (Ctrl + right click) (default is 'offset').
        sync_chan : list
            List of channels to synchronise vertical scales. The length of sync_chan
            should be equal to the number of displayed channels, and specify, for
            each channel, the list of channels to synchronize. For example, the
            default list [[0,1],[0,1],[2,3],[2,3]] synchronizes channels 0 and 1,
            and channels 2 and 3. Set sync_chan to [[0],[1],[2],[3]] for no
            synchronization of vertical scales (default is [[0,1],[0,1],[2,3],[2,3]]).
        group_chan : bool
            if True, group channels plots of synchronized channels. Can only apply
            to contiguous channels, if non contiguous channels are synchronized,
            group_chan is set to False (default is True).
        list_trials : list
            List of trials to display, if None, display all trials (defauls is
            None).
        random_order: bool
            If True, display trials in random order (note that epoch number in
            viz window does not correspond to true epoch number in that case). 
        """
        
        # reinitializes UI if reloading data 
        if hasattr(self.window,'data'):
            self.window = VizUi()
        
        if len(data.shape) > 2:
            # import warnings 
            # warnings.simplefilter('default')
            # warnings.warn('\nMyonset.viz now loads continuous instead of segmented data, to avoid future error, provide :\n\t2D data (times x channels), continuous events, code_t0 (event code(s) defining trials), tmin and tmax times.\n', DeprecationWarning)
            print('\nWARNING ! Myonset.viz now loads continuous instead of segmented data, to avoid future error, provide :\n\t2D data (times x channels), continuous events, code_t0 (event code(s) defining trials), tmin and tmax times.\n')
            
            print('Do you wish to continue and create continuous events and data from epochs (at your own risks !) ? (y)es / (n)o')
            answer = input()
            
            if answer == 'y':
                if hasattr(code_t0,'list_evts_trials'):
                    events = code_t0 # really not nice bu useful as arguments are ordered differentky in previous version

                code_t0 = []
                for t in range(events.nb_trials()):
                    code_t0.extend(events.list_evts_trials[t].find_and_get_events(time=0, print_find_evt=False).code)
                code_t0 = np.unique(code_t0)
                print(('Finding time 0 events: codes are {} ').format(code_t0))


                print('Going back to continuous events...')
                continuous_events = events.as_continuous()[0]
                
                continuous_data = np.zeros((data.shape[1], np.max(events.tmax.sample)+1))
                for t in range(events.nb_trials()):
                    continuous_data[ : , events.tmin.sample[t]:events.tmax.sample[t]+1] = data[t]
                print(('Creating continuous data: new shape is {}').format(continuous_data.shape))

                data = continuous_data
                events = continuous_events
            
        self.window.load_data(data, events, code_t0, tmin=tmin, tmax=tmax, channels=channels, code_movable_1=code_movable_1 , code_movable_2=code_movable_2 , sync_chan=sync_chan, group_chan=group_chan, list_trials=list_trials, random_order=random_order)
        
    def show(self):
#        self.window.w.show()
        self.window.show()
#        sys.exit(self.exec_())
        self.exec_() # For Spyder Users
        
    def get_events(self):
        return self.window.get_events()

    def get_epoch_events(self):
        return self.window.get_epoch_events()

    
def main():

#    app = QApplication(sys.argv)
    ex = VizApplication(sys.argv)
    ex.show()

if __name__ == '__main__':
    main()