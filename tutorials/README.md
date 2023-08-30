# Tutorials for Myonset Package

Myonset is a python package to process and detect signal burst(s) onset and offset, especially developed for electromyographic (EMG) signal. 
Myonset implements tools for signal preprocessing, automatic onset and offset detection, as well as vizualisation and correction of onset and offset latencies.

### Available tutorials

Tutorials ara available as Jupyter Notebook. To run tutorials, download the corresponding notebook and the associated data (if you are not sure which data file you need, downlad all files starting with 'example_...').

- Tutorial 1 illustrates how to load datafile and preprocess EMG signal using myonset:
    1. Load data file, file formats: text file, bdf (biosemi) file, brain vision (.vhdr) file or edf file. More formats are available using the mne package, you will just have to use the appropriate mne function in cell 3.

    2. Extract events (i.e., triggers): events are time markers specifying the exact time positions of specific events like stimulus or response in (continuous) data recording. In the case of text files, events are stored in separate csv file, for other formats, events are stored in the same file as data signal.

    3. Compute bipolar reference: for each EMG channel, compute the difference between the two electrodes. In tutorial examples, we compute the difference between 'EXG1' and 'EXG2', electrodes placed on left hand, and 'EXG3' and 'EXG4', electrodes placed on right hand.

    4. Filter data signal, here 10 Hz high pass filter is applied

    5. Extract data array and save it in .npy file.

- Tutorial 2 presents the Events structure, our basic container object to store and manage events (i.e., event markers / triggers). Events management is important in myonset because that is where we will store the result of signal burst onsets and offsets.

- Tutorial 3 shows how to run automatic detection on preprocessed data file from tutorial 1.

- Tutorial 4 shows how to vizualise and correct burst onsets and offsets detected automatically. 




