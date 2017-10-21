
import serial
import queue
import sys
import time
import re
from threading import Thread

class Robot:
    def __init__(self, port=None):
        self.port = port
        self.ser = serial.Serial(baudrate=115200)
        if port:
            self.ser.port = port
            self.ser.open()
        self.cmd_queue = queue.Queue()
        self.worker = Thread(target=self.send_thread)
        self.worker.start()

    def mix(self, ingredients):
        for amount, positions in ingredients:
            best = (-1, -1)
            for pos, reserve in positions:
                if (reserve > amount + 40 and
                    (best[1] < 0 or reserve < best[1])):
                    best = (pos, reserve)
            positions[:] = [best]
        ingredients.sort(key=lambda x:x[1][0])
        self.sendCmd(b"\n".join((self.gcode(pos, amount, reserve) for
                                 amount, ((pos, reserve),) in ingredients)))
                
    def readResponse(self):
        while True:
            if self.ser.in_waiting:
                res = self.ser.readline()
                #print(res.decode("utf8"))
                if b"ok" in res:
                    return 0
                m = re.search(br"error:(\d+)", res)
                if m:
                    return int(m.group(1))

    def sendCmd(self, cmd):
        cmd = cmd.split(b"\n")
        self.cmd_cnt = 0
        for l in cmd:
            l = l.strip()
            self.cmd_queue.put(l + b"\n")
            self.cmd_cnt += 1

    def wait(self):
        self.cmd_queue.join()

    def progress(self):
        if self.cmd_cnt:
            return float(self.cmd_queue.qsize()) / self.cmd_cnt
        else:
            return 1.0

    def busy(self):
        return self.cmd_queue.qsize() > 0

    def send_thread(self):
        while True:
            cmd = self.cmd_queue.get()
            print(cmd.strip().decode("utf8"), end=' ')
            self.ser.write(cmd)
            print(self.readResponse() or "ok")

if __name__ == "__main__":

    r = Robot("/dev/ttyUSB0")
    r.ser.write(b"?\n")
    while True:
        cmd = sys.stdin.readline()
        r.sendCmd(cmd.encode("utf8"))
        
        
    
    
