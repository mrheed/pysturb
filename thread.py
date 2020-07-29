import sys
import thread
import time

class Thread:
    def __init__(self):
        pass

    def run(self, thread):
        pass

    def startProgress(self, title):
        global progress_x
        sys.stdout.write(title + ": [" + "-"*100 + "]" + chr(8)*101)
        sys.stdout.flush()
        progress_x = 0
    
    def progress(self, x):
        global progress_x
        x = int(x * 100 // 100)
        sys.stdout.write("#" * (x - progress_x))
        sys.stdout.flush()
        progress_x = x
    
    def endProgress(self):
        sys.stdout.write("#" * (100 - progress_x) + "\n")
        sys.stdout.flush()
    

x = Thread()
x.startProgress("Title")
for i in range(100):
    x.progress(i+1)
x.endProgress()

