"""
Copyright (C) 2017 - The CocktailOverlord Authors

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import serial
import queue
import sys
import time
import re
import glob
from threading import Thread

class Robot:
    def __init__(self, port=None):
        self.cmd_cnt = 0
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
                if (reserve >= amount and
                    (best[1] < 0 or reserve < best[1])):
                    best = (pos, reserve)
            positions[:] = [best]
        ingredients.sort(key=lambda x:x[1][0])
        self.sendCmd(b"\n".join((self.gcode(pos, amount, reserve) for
                                 amount, ((pos, reserve),) in ingredients)))

    def autoconnect(self):
        self.sendCmd(b"##CONNECT")

    def disconnect(self):
        self.sendCmd(b"##DISCONNECT")

    def _connect(self):
        for device in glob.glob('/dev/ttyUSB*'):
            self.ser.port = device
            try:
                self.ser.open()
            except: # XXX
                print("Could not open device", device)
                continue
            self.ser.write(b"?\n")
            time.sleep(3.0)
            result = self.ser.read_all()
            print(result)
            self.ser.write(b"$X\n")
            if result:
                break
        else:
            print("No robot found")
            pass

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
            if cmd.startswith(b"##"):
                if cmd == b"##CONNECT\n":
                    print("##Connect")
                    self._connect()
                if cmd == b"##DISCONNECT\n":
                    self.ser.close()
                    while not self.cmd_queue.empty():
                        self.cmd_queue.get(block=False)
                    self.cmd_cnt = 0
            else:
                print(cmd.strip().decode("utf8"), end=' ')
                self.ser.write(cmd)
                print(self.readResponse() or "ok")

if __name__ == "__main__":

    r = Robot("/dev/ttyUSB0")
    r.ser.write(b"?\n")
    while True:
        cmd = sys.stdin.readline()
        r.sendCmd(cmd.encode("utf8"))
        
        
    
    
