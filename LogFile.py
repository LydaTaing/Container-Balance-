# path, buffer, startTime
# get current time to string 
# creat log file
# logging with the input string of message from the system
# stop logging

import datetime
import os

class LogFile:
    def __init__(self):
        self.filePath = None
        self.buffer = []
        self.startTime = datetime.datetime.now()

    def Time2String(self):
        time = datetime.datetime.now()
        return time.strftime("%m %d %y: %H:%M")

    def createLog(self, filePath):
        
        #create a log folder
        if not os.path.exists("logs"):
            os.makedirs("logs")
        
        #get only the file name without extension
        name = os.path.splitext(os.path.basename(filePath))[0]
        
        # get the starting time and create the file name for solution 
        filetime = self.startTime.strftime("_%m_%d_%y_%H%M")
        # create the full path with file name
        self.filePath = os.path.join("logs", f"{name}{filetime}.txt")
        
        #get buffer message and system action
        try:
            with open(self.filePath, "w") as file:
                for b in self.buffer:
                    file.write(b)
            
            #clear the buffer
            self.buffer = []
            print(f"Log file was created: {self.filePath}")                        
        except Exception as e:
            print(f"Error to create file: {e}")
        
    def logging(self, msg):
        time = self.Time2String()
        text = f"{time} {msg}"
        
        #check for the existing file
        if self.filePath:
            with open(self.filePath, "a") as file:
                file.write(text + "\n")
        else:
            self.buffer.append(text)
        
    def closeLog(self):
        self.logging("Program is shutting down.")