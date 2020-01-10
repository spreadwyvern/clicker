import sys
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import QThread
from clicker import *

import threading
from threading import Timer

from pynput.keyboard import Key, KeyCode, Listener, Controller
import os
import sys
import time
from datetime import datetime
import pandas as pd

from winsound import PlaySound, SND_FILENAME, SND_LOOP, SND_ASYNC

# get relative path for compiling into one file
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)


class WorkerSignals(QObject):
    '''
    Defines the signals available from a running worker thread.

    Supported signals are:

    finished
        No data

    error
        `tuple` (exctype, value, traceback.format_exc() )

    result
        `object` data returned from processing, anything

    '''
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    result = pyqtSignal(object)
    progress = pyqtSignal(object)


class Worker(QThread):
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
        # self.fn(*self.args, **self.kwargs)
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

class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        # self.threadpool = QThreadPool()
        self.fileName = None
        self.threads = []
        self.keyboard = Controller()
        self.debugPrint('Current alarm tone: {}'.format(self.signalBox.currentText()))
        self.alarm_type = self.signalBox.currentText()
        self.returnedPressedPath()
        self.recorder = None





    def selectionchange(self,i):
        self.debugPrint("Chosen alarm tone: {}".format(self.signalBox.currentText()))
        self.alarm_type = self.signalBox.currentText()

    def returnedPressedPath(self):
        self.fileName = self.outputPath.text()
        if self.fileName[-3:] == 'csv':
            self.debugPrint("record will be stored to: {}".format(self.fileName))
        else:
            m = QtWidgets.QMessageBox()
            m.setText("Invalid file format!\nRecord file should be in csv format!")
            m.setIcon(QtWidgets.QMessageBox.Warning)
            m.setStandardButtons(QtWidgets.QMessageBox.Ok)
            ret = m.exec_()
            self.outputPath.setText( "" )
            # self.refreshAll()
            self.debugPrint( "Invalid file format specified: {}".format(self.fileName.split('.')[-1]))
    
    def debugPrint(self, msg):
        self.textBrowser.append(msg)
    
    # slot
    def browseButtonClicked(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        self.fileName, _ = QFileDialog.getOpenFileName(self, "Select output file", "",
                                                  "csv file (*.csv)", options=options)
        if self.fileName:
            self.outputPath.setText(self.fileName)
            self.debugPrint("record will be stored to: {}".format(self.fileName))

    def startButtonClicked(self):
        # print('start clicked')
        if not self.fileName:
            m = QtWidgets.QMessageBox()
            m.setText("Unassigned record path!\nAssign file path before recording!")
            m.setIcon(QtWidgets.QMessageBox.Warning)
            m.setStandardButtons(QtWidgets.QMessageBox.Ok)
            ret = m.exec_()
            
            # self.refreshAll()
            self.debugPrint( "Unspecified output file!")
        else:       
            self.recorder = Recorder()
            self.recorder.get_path(self.fileName)
            self.recorder.get_alarm(self.alarm_type)
            
            self.worker = Worker(self.recorder.listener)
            # self.threadpool.start(self.worker)
            self.worker.start()
            self.threads.append(self.worker)
            self.worker.signals.finished.connect(self.thread_complete)
            self.worker.signals.result.connect(self.debugPrint)
            self.worker.signals.progress.connect(self.debugPrint)
      
            # execute
            self.debugPrint("Start recording")
            self.recordIndicator.setText('= Recoding! =')

    def send_signal(self):
        self.keyboard.press('s')

    def automatic_toner(self, progress_callback):
        while True:
            t = Timer(5, self.send_signal)
            t.start()  

    def startTestClicked(self, interval=5):
        if not self.recorder:
            self.debugPrint("Start recorder first before clicking start test button!")
        else:
            # self.toner = RepeatingTimer(5)
            # self.toner.get_alarm(self.alarm_type)
            # self.worker_toner = Worker(self.toner.run)
            # self.worker_toner.start()
            # self.threads.append(self.worker_toner)
            # self.worker_toner.signals.progress.connect(self.debugPrint)
            self.thread = QThread()
            self.toner = Toner()
            self.toner.get_alarm(self.alarm_type)
            self.toner.moveToThread(self.thread)
            self.thread.started.connect(self.toner.task)
            self.thread.start()

    def endTestClicked(self):
        if not (self.toner & self.thread):
            self.debugPrint('Not recording!')
        else:
            self.toner.stop()
            self.thread.quit()
            self.thread.wait()

    def toner(self):
        while True:
            t = Timer(interval, self.keyboard.press('s'))
            t.start()  

    def endButtonClicked(self):
        # pass the function to execute
        self.keyboard.press(Key.esc)
        self.keyboard.release(Key.esc)
        self.recordIndicator.setText('Not Recording')

    def thread_complete(self):
        self.debugPrint("Recorder Stopped!")

class Toner(QObject):
    'Object managing the simulation'

    def __init__(self):
        super(Toner, self).__init__()
        self._step = 0
        self._isRunning = True
        self._maxSteps = 20
        self.keyboard = Controller()
    
    def get_alarm(self, alarm_type):
        if alarm_type == 'Intermittent':
            self.alarm = resource_path('iso8201_lf_10s.wav')
        elif alarm_type == 'Continuous':
            self.alarm = resource_path('500hz_cont_10s.wav')
   
    @pyqtSlot()
    def task(self):
        if not self._isRunning:
            self._isRunning = True
        while self._isRunning == True:
            self.keyboard.press('s')
            time.sleep(8)

    @pyqtSlot()
    def stop(self):
        self._isRunning = False

class RepeatingTimer(object):
    def __init__(self, interval_seconds):
        self.interval_seconds = interval_seconds
        self.stop_event = True
        self.keyboard = Controller()
 
    def get_alarm(self, alarm_type):
        if alarm_type == 'Intermittent':
            self.alarm = resource_path('iso8201_lf_10s.wav')
        elif alarm_type == 'Continuous':
            self.alarm = resource_path('500hz_cont_10s.wav')
 
    def run(self, progress_callback):
        self.progress_callback = progress_callback
        while True:
            self.keyboard.press('s')
            self.progress_callback.emit('automated')
            time.sleep(self.interval_seconds)
            
    def stop(self):
        return False

class Recorder(object):

    def __init__(self):
        self.keyboard = Controller()

    def get_alarm(self, alarm_type):
        if alarm_type == 'Intermittent':
            self.alarm = resource_path('iso8201_lf_10s.wav')
        elif alarm_type == 'Continuous':
            self.alarm = resource_path('500hz_cont_10s.wav')
    
    def get_path(self, record_path):
        self.record_path = record_path

    def record(self, key, pressed_time, record_path):
        click_tmp = pd.DataFrame({'button': str(key), 'time': pressed_time}, index=[0])
        if os.path.exists(self.record_path):
            click_record = pd.read_csv(record_path)
            click_record = pd.concat([click_record, click_tmp])
            click_record.to_csv(self.record_path, index=False)
            del click_record, click_tmp
        else:
            click_tmp.to_csv(self.record_path, index=False)
            del click_tmp

    def on_press(self, key):
        if key == KeyCode.from_char('s'):
            pressed_time = datetime.fromtimestamp(time.time())
            self.record(key, pressed_time, self.record_path)
            self.progress_callback.emit('Signaled at {}'.format(pressed_time))
            PlaySound(self.alarm, SND_FILENAME|SND_ASYNC)
        elif key == KeyCode.from_char('r'):
            pressed_time = datetime.fromtimestamp(time.time())
            self.record(key, pressed_time, self.record_path)
            self.progress_callback.emit('Responsed at {}'.format(pressed_time))
            PlaySound(None, SND_FILENAME)
    def on_release(self, key):
        if key == Key.esc:
            self.progress_callback.emit('Stop recording')
            # Stop listener
            return False
    # def on_scroll(x, y, dx, dy):
    #     print('Scrolled {0} at {1}'.format(
    #         'down' if dy < 0 else 'up',
    #         (x, y)))

    # Collect events until released

    def listener(self, progress_callback):
        self.progress_callback = progress_callback
        with Listener(
                on_press=self.on_press,
                on_release = self.on_release,
                ) as listener:
            listener.join()
        
        # # different method
        # self.listener = mouse.Listener(
        #     on_click=self.on_click
        #     )
        # self.listener.start()
    def stop_recording(self):
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())