import sys
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import QThread

# import UI layout
from clicker_simple import *

# keyboard control
from pynput.keyboard import Key, KeyCode, Listener, Controller
# sound playback control
from winsound import PlaySound, SND_FILENAME, SND_LOOP, SND_ASYNC

from threading import Thread
import os
import sys
import time
from datetime import datetime
import pandas as pd

class AutoSignal(QObject):
    '''
    Automatically send signal to the patient event receptor on EEG.
    There are two types of signals:
    1. automatic signal to check the conscioussness of the patient
    2. synchronizing beeps to help synchronize time of EEG and the recording laptop

    '''

    def __init__(self):
        super(AutoSignal, self).__init__()
        self._isRunning = True
        self.keyboard = Controller()
    
        self._mutex = QMutex()
        self._running = True
     
    # set up baseline by signaling every 30 senconds, then automatically signal every 5 minutes (300 s)
    def timed(self):
        steps = 0
        while self.running():
            self.keyboard.press(Key.f17)
            self.keyboard.press(Key.num_lock)
            self.keyboard.release(Key.num_lock)
            self.keyboard.press(Key.num_lock)
            self.keyboard.release(Key.num_lock)
            if steps < 5:
                time.sleep(30)
                steps = steps + 1
            else:
                time.sleep(300)
                steps = steps + 1

    # syncing beeps every 10 seconds
    def sync_beep(self):
        while self.running():
            self.keyboard.press(Key.scroll_lock)
            self.keyboard.release(Key.scroll_lock)
            self.keyboard.press(Key.scroll_lock)
            self.keyboard.release(Key.scroll_lock)

            time.sleep(10)

    @pyqtSlot()
    def task(self):
        timedThread = Thread(target=self.timed)
        syncThread = Thread(target=self.sync_beep)
        syncThread.start()
        timedThread.start()

    @pyqtSlot()
    def stop(self):
        self._mutex.lock()
        self._running = False
        self._mutex.unlock()

    def running(self):
        try:
            self._mutex.lock()
            return self._running
        finally:
            self._mutex.unlock()


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.
    Supported signals are:
    finished
        No data
    error
        `tuple` (exctype, value, traceback.format_exc() )
    result
        object` data returned from processing, anything
    progress
        object` data returned from processing, anything
    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)


class Worker(QThread):
    '''
    Subclassing QThread for more controls of threading
    '''
    def __init__(self, fn, *args, **kwargs):
        super(Worker, self).__init__()
        self.args = args
        self.kwargs = kwargs
        self.fn = fn
        self.signals = WorkerSignals()

        # Add the callback to kwargss
        self.kwargs['progress_callback'] = self.signals.progress
        self.threadactive = True

    @pyqtSlot()
    def run(self):
        try:
            result = self.fn(*self.args, **self.kwargs)
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)
        finally:
            self.signals.finished.emit()


# get relative path for compiling into one file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# the recorder
class Recorder(object):
    '''
    Monitoring the below keyboard inputs and record the corresponding event
    F15 as technician signal
    F16 as patient response
    F17 as automatic signal
    Scroll lock as syncing signal
    in the recording csv file, 'event' column records each event with label
    'tech', 'patient', 'auto', 'sync'
    '''

    def __init__(self):
        self.keyboard = Controller()
        self.alarm = resource_path('200.wav')
    
    def get_path(self, record_path):
        self.record_path = record_path

    def get_patient_id(self, patient_id):
        self.patient_id = patient_id

    # wrtie data to csv file
    def record(self, event, pressed_time, record_path):
        click_tmp = pd.DataFrame({'patient': self.patient_id, 'event': event, 'time': pressed_time}, index=[0])
        if os.path.exists(self.record_path):
            click_record = pd.read_csv(record_path)
            click_record = pd.concat([click_record, click_tmp])
            click_record.to_csv(self.record_path, index=False)
            del click_record, click_tmp
        else:
            click_tmp.to_csv(self.record_path, index=False)
            del click_tmp

    # monitor key pressing event
    def on_press(self, key):
        if key == Key.f15:
            pressed_time = datetime.fromtimestamp(time.time())
            self.record('tech', pressed_time, self.record_path)
            self.progress_callback.emit('Signaled at {}'.format(pressed_time))
            # play alarm sound
            PlaySound(self.alarm, SND_FILENAME|SND_ASYNC)
        elif key == Key.f16:
            pressed_time = datetime.fromtimestamp(time.time())
            self.record('patient', pressed_time, self.record_path)
            self.progress_callback.emit('Responsed at {}'.format(pressed_time))
            # stop alarm sound
            PlaySound(None, SND_FILENAME)
        elif key == Key.f17:
            pressed_time = datetime.fromtimestamp(time.time())
            self.record('auto', pressed_time, self.record_path)
            self.progress_callback.emit('Automatic signal at {}'.format(pressed_time))
            PlaySound(self.alarm, SND_FILENAME|SND_ASYNC)
        elif key == Key.scroll_lock:
            pressed_time = datetime.fromtimestamp(time.time())
            self.record('sync', pressed_time, self.record_path)

    def on_release(self, key):
        if key == Key.esc:
            # stop the alarm sound
            PlaySound(None, SND_FILENAME)
            # Stop listener
            return False

    # listen to events until recorder stops
    def listener(self, progress_callback):
        self.progress_callback = progress_callback
        with Listener(
                on_press=self.on_press,
                on_release = self.on_release,
                ) as listener:
            listener.join()