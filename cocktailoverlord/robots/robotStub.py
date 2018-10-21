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
from enlightment.enlight import Enlightment
from threading import Thread

class SerFake:
    def isOpen(self):
     return True

class Robot:
    def __init__(self, ports=None):
        self.enlight = Enlightment()
        self.cmd_cnt = 0
        self.ser = SerFake()# serial.Serial(baudrate=115200)
        self.state = "offline"
        self.cmd_queue = queue.Queue()
        self.worker = Thread(target=self.send_thread)
        self.worker.start()
        if ports:
            self._connect(ports)

    def mix(self, ingredients):
        print("mix called: " + str(ingredients))
        self.enlight.setMixing([i[1][0][0] for i in ingredients])
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

    def _connect(self, ports=None):
        print("_connect called")
        if not ports:
            ports = glob.glob('/dev/ttyUSB*')
        for i in range(5):#device in ports:
            self.state = "connecting"
#            self.ser.port = device
            try:
                pass
#                self.ser.open()
            except: # XXX
                print("Could not open device", device)
                continue
#            self.ser.write(b"?\n")
            start = time.time()
            result = b""
            while True:
#                result += self.ser.read_all()
                if True:# or result.find(b"[MSG:'$H'|'$X' to unlock]") >= 0:
                    self.state = "connected"
                    print("connected")
                    break
                if time.time() - start > 15.:
                    break
#            print("result: " + result)
#            self.ser.write(b"$X\n")
            if self.state == "connected":
                break
        else:
            self.state = "offline"
            print("No robot found")

    def readResponse(self):
        return 0
#        while True:
#            print("fake response")
#            return 0
#            if self.ser.in_waiting:
#                res = self.ser.readline()
#                #print(res.decode("utf8"))
#                if b"ok" in res:
#                    return 0
#                m = re.search(br"error:(\d+)", res)
#                if m:
#                    return int(m.group(1))

    def sendCmd(self, cmd):
        print("send CMD: " + str(cmd))
        self.state = "busy"
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
         self.enlight.stopMixing()
         return 1.0

    def busy(self):
        return self.cmd_queue.qsize() > 0

    def send_thread(self):
        while True:
            cmd = self.cmd_queue.get()
        #    print("queueu: " + str(cmd))
            if cmd.startswith(b"##"):
                if cmd == b"##CONNECT\n":
                    print("##Connect")
                    self._connect()
                if cmd == b"##DISCONNECT\n":
                    self.state = "offline"
        #            self.ser.close()
                    while not self.cmd_queue.empty():
                        self.cmd_queue.get(block=False)
                    self.cmd_cnt = 0
            else:
                print("strip stuff" + cmd.strip().decode("utf8"), end=' ')
        #        self.ser.write(cmd)
#                print(self.readResponse() or "ok")
                if self.cmd_queue.empty(): # XXX not on error
                    self.state = "ready"

