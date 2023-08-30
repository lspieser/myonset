# Myonset Package

Myonset is a python package to process and detect signal burst(s) onset and offset, especially developed for electromyographic (EMG) signal. 
Myonset implements tools for signal preprocessing, automatic onset and offset detection, as well as vizualisation and correction of onset and offset latencies.

### Installation

Dependencies

Myonset toolbox requires Python 3 installation, installing Anaconda is recommended, but any other Python 3 installation should work. Most Myonset dependencies are provided with a base Anaconda environment (numpy, scipy, matplotlib, PyQt5). 
The only package that needs to be installed (when using Anaconda...) is pyqtgraph (installation instruction below).

Installing through Anaconda

Open the anaconda prompt (Windows: Applications / Anaconda 3 / Anaconda prompt ; Mac /linux: just start a terminal).
First, install pyqtgraph:
```
conda install pyqtgraph
```

Most users will also need mne-python, on which we mainly rely to open and save files containing EMG data signal:
```
pip install mne
```

Finally, install Myonset: copy folder ‘myonset_pck’ somewhere on your computer, then in anaconda prompt:
```
pip install ‘PATH_OF_MYONSET_PCK_FOLDER’
```
	
For instance:
```
pip install C:\Users\Administrateur\Downloads\myonset_pck
```	

### License

Myonset is licensed under the GNU General Public Licence v3 - see COPYING file for more details.


