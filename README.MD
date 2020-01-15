# Clicker Recorder
## Introduction
A recording application for clicker system
## Requirements
Python 3 and Windows OS
```
pip install -r requirements.txt
```
## Usage
Execute the python script,
```
python clicker.py
```
or run the compiled executable clicker.exe file in 'dist' folder.

## Description
The main app is the clicker.py which calls clicker_ui.py for the layout of UI.
Core functions are in utils.py which consists of the AutoSignal and Recorder classes.
### AutoSignal
Automatically send signal to the patient event receptor on EEG.
There are two types of signals:
1. automatic signal to check the conscioussness of the patient
2. synchronizing beeps to help synchronize time of EEG and the recording laptop

### Recorder
Monitors the below keyboard inputs and record the corresponding event
F15 as technician signal
F16 as patient response
F17, num_lock as automatic signal
Scroll lock as syncing signal
in the recording csv file, 'event' column records each event with label 'tech', 'patient', 'auto', 'sync'
*note: the control box can receive caps_lock, num_lock and scoll_lock inputs from the PC, so I use it as a way to let PC to send signal from the PC to control the relay. However, it takes two press-release event of num_lock to turn on and off the relay. Thus to avoid recorder recording a duplicate event I use F17 as the key for recorder to monitor*


## Default input and output files
The default ouput file is clicker_recorder.csv, this can be modified in line 27 of clicker.py
Default alarm tone is 200.wav, this can be changed in line 160 of utils.py

