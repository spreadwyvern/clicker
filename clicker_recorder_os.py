import sys
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import QThread
from clicker import *
from recorder import Recorder
from utils import play_sound, stop_sound

import threading

from pynput.keyboard import Key, KeyCode, Listener, Controller
import os
import time
from datetime import datetime
import pandas as pd

from winsound import PlaySound, SND_FILENAME, SND_LOOP, SND_ASYNC

import pyaudio

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

        # Add the callback to kwargs
        self.kwargs['progress_callback'] = self.signals.progress

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


    def endButtonClicked(self):
        # pass the function to execute
        self.keyboard.press(Key.esc)
        self.keyboard.release(Key.esc)
        self.recordIndicator.setText('Not Recording')

    def thread_complete(self):
        self.debugPrint("Recorder Stopped!")

class Recorder():

    # def __init___(self, fq, sounds):
    
    def get_alarm(self, alarm_type):
        if alarm_type == 'Intermittent':
            self.alarm = 'iso8201_lf_10s.wav'
        elif alarm_type == 'Continuous':
            self.alarm = '500hz_cont_10s.wav'
    
    def get_path(self, record_path):
        self.record_path = record_path

    def play_alarm_file(self):
        """Simple callback function to play a wave file. By default it plays
        a Ding sound.

        :param str fname: wave file name
        :return: None
        """
        ding_wav = wave.open(self.alarm, 'rb')
        ding_data = ding_wav.readframes(ding_wav.getnframes())
        audio = pyaudio.PyAudio()
        stream_out = audio.open(
            format=audio.get_format_from_width(ding_wav.getsampwidth()),
            channels=ding_wav.getnchannels(),
            rate=ding_wav.getframerate(), input=False, output=True)
        stream_out.start_stream()
        stream_out.write(ding_data)
        time.sleep(0.2)
        stream_out.stop_stream()
        stream_out.close()
        audio.terminate()     

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
            PlaySound(self.alarm, SND_FILENAME|SND_LOOP|SND_ASYNC)
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