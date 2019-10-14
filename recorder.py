from pynput import mouse
import os
import time
from datetime import datetime
import pandas as pd

# def on_move(x, y):
#     print('Pointer moved to {0}'.format(
#         (x, y)))
def main():
    recorder = Recorder()
    recorder.get_path('clicker_record.csv')
    recorder.listener()

class Recorder():

    # def __init___(self, record_path):
    #     self.record_path = record_path

    def get_path(self, record_path):
        self.record_path = record_path

    def record(self, button, pressed_time, record_path):
        click_tmp = pd.DataFrame({'button': str(button), 'time': pressed_time}, index=[0])
        if os.path.exists(self.record_path):
            click_record = pd.read_csv(record_path)
            click_record = pd.concat([click_record, click_tmp])
            click_record.to_csv(self.record_path, index=False)
            del click_record, click_tmp
        else:
            click_tmp.to_csv(self.record_path, index=False)
            del click_tmp

    def on_click(self, x, y, button, pressed):
        # pressed_time = datetime.fromtimestamp(time.time())
        

        if pressed:
            # using timestamp for quicker response
            pressed_time = time.time()
            self.record(button, pressed_time, self.record_path)
            print('{0} {1} at {2}'.format(
                'Pressed',
                button, pressed_time))

        # if not pressed:
        #     # Stop listener
        #     return False

    # def on_scroll(x, y, dx, dy):
    #     print('Scrolled {0} at {1}'.format(
    #         'down' if dy < 0 else 'up',
    #         (x, y)))

    # Collect events until released
    def listener(self):
         with mouse.Listener(
                on_click=self.on_click
                ) as listener:
            listener.join()
        
        # # different method
        # self.listener = mouse.Listener(
        #     on_click=self.on_click
        #     )
        # self.listener.start()
    def stop_recording(self):
        return False

if __name__ == '__main__':
    main()