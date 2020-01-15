import sys
import traceback
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.Qt import QThread

# import UI layout
from clicker_ui import *
'''
import utilities: Recorder, AutoSignal
The Recorder class object is in charge of monitoring and recording keyboard inputs.
The AutoSignal class object is in charge of sending automatic signals.
'''
from utils import *


# Main UI class
class MyMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None):
        super(MyMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.setWindowTitle("Clicker")


        # output csv path
        self.fileName = 'click_record.csv'
        self.threads = []
        self.keyboard = Controller()
        self.recording = False

       # connect buttons to custom button functions
        self.startTest.clicked.connect(self.startTestClicked)
        self.endTest.clicked.connect(self.endTestClicked)
    
    # print message to main text box    
    def debugPrint(self, msg):
        self.textBrowser.append(msg)

    # start button function
    def startTestClicked(self):
        '''
        First check if patient ID is given, then check if the recorder is already running.
        Creat a Recorder class object and move to a Worker (custom Qthread), then creat a AutoSignal class and move it
        to a Qthread.
        '''
        # check if patient ID is given
        if self.patientID.text() == '':
            m = QtWidgets.QMessageBox()
            m.setWindowTitle("No patient ID")
            m.setIcon(QMessageBox.Warning)
            m.setText("Enter patient ID before recording.")
            m.setIcon(QtWidgets.QMessageBox.Warning)
            m.setStandardButtons(QtWidgets.QMessageBox.Ok)
            ret = m.exec_()
        else:
            # check if recorder is already running
            if self.recording == False:
                self.recording = True
                self.recorder = Recorder()
                self.recorder.get_path(self.fileName)
                self.recorder.get_patient_id(self.patientID.text())
                self.debugPrint('Patient ID: {}'.format(self.patientID.text()))
                
                self.worker = Worker(self.recorder.listener)
                self.worker.start()
                self.worker.signals.finished.connect(self.thread_complete)
                self.worker.signals.result.connect(self.debugPrint)
                self.worker.signals.progress.connect(self.debugPrint)
          
                # sent messages to main UI and text box
                self.debugPrint("Start recording")
                self.recordIndicator.setText('= Recoding! =')
         
                self.thread = QThread()
                self.auto_signal = AutoSignal()
                self.auto_signal.moveToThread(self.thread)
                self.thread.started.connect(self.auto_signal.task)
                self.thread.start()
            else:
                self.debugPrint('Already recording!')
    
    # end button function
    def endTestClicked(self):
        '''
        Check if recorder is running, send out a keyboard ESC signal to terminate the recorder.
        Stop the auto_signal.
        Clear patient ID input box to prevent users from forgetting to change patient ID for a new patient.
        '''
        if self.recording:
            self.keyboard.press(Key.esc)
            self.keyboard.release(Key.esc)

            # change main UI display
            self.recordIndicator.setText('Not Recording')
            self.auto_signal.stop()

            self.thread.quit()
            self.thread.wait()

            # clear patient ID box
            self.patientID.clear()

            self.recording = False
        else:
            self.debugPrint('Not recording now.')
            

    def thread_complete(self):
        self.debugPrint("Recorder Stopped!")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    myWin = MyMainWindow()
    myWin.show()
    sys.exit(app.exec_())