import datetime
import os


class Date_time():
    def __init__(self):
        self.year = 2024
        self.month = 1
        self.day = 1
        self. hour = 11
        self.minute = 0
        self.second = 0


    def set_system_time(self):
        new_time = datetime.datetime(self.year, self.month, self.day, self.hour, self.minute, self.second)
        formatted_time = new_time.strftime('%Y-%m-%d %H:%M:%S')
        os.system(f'sudo date -s "{formatted_time}"')



datetime1 = Date_time()
datetime1.set_system_time()


