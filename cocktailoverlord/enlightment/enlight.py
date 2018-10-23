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


import os, serial, sys, time, glob, random, colorsys, importlib
from threading import Thread

def log(s):
 print("Enlighter says: " + str(s))
def checkColor(v):
 return v >= 0 and v < 256

def adjBrightness(colors, b):
 for k, v in colors.items():
  colors[k] = tuple(map(lambda c: int(c*b), v))

def mixAnim(colors, c,  frame, idxs):
 steps =9
 bottom = .5
 myrange = 1.-bottom
 step = myrange/steps
 frame %= (steps*2)
 
 for i in range(len(colors)):
  colors[i] = c
  if i in idxs:
   hsvc = colorsys.rgb_to_hsv(colors[i][0],colors[i][1],colors[i][2])
   v = hsvc[2]
   if (frame < steps):
    v = bottom + frame*step
   else:
    v = 1-(frame%steps*step)
   colors[i] = tuple(map(lambda x: int(255*x), colorsys.hsv_to_rgb(hsvc[0]+.5, hsvc[1], v)))
 

def alertAnim(colors, frame, idxs):
 steps =3
 bottom = .5
 myrange = 1.-bottom
 step = myrange/steps
 frame %= (steps*2)
 
 for i in range(len(colors)):
  if i in idxs:
   if (frame < steps):
    v = bottom + frame*step
   else:
    v = 1-(frame%steps*step)
   colors[i] = tuple(map(lambda x: int(255*x), colorsys.hsv_to_rgb(0, 1, v)))
 



class Enlightment:
 def __init__(self):
  self.readConfig()
  self.colors = {}
  self.device = "asdf"
  self.ser = serial.Serial("/dev/ttyUSB0", timeout=.01,baudrate=115200)

  for i in range(int(self.configMap['nbrBottles'])):
   self.setColor(i, 0,0,0)
  self.mixingIdxs = None

  self.loadBGAnims()
  self.setBgAnim(self.bgAnimFuncs[0])

  self.worker = Thread(target=self.thread_loop)
  self.worker.daemon = True
  self.worker.start()
  print(self.configMap)

 def loadBGAnims(self):
  files = []
  for (dirpath, dirname, filenames) in os.walk("enlightment/anims/bg/active"):
   files.extend(filenames)
  files = filter(lambda fn: not fn.startswith("__"), files)
  files = filter(lambda fn: not fn.endswith("pyc"), files)
  files = map(lambda fn: fn.strip(".py"), files)
  funcs = []
  for f in files: 
   #funcs.append(importlib.import_module("enlightment.anims.bg.active."+str(f), package=None).anim)
   funcs.append(importlib.import_module("anims.bg.active."+str(f), package=None).anim)
  self.bgAnimFuncs = funcs  


 def setBgAnim(self, fp):
  self.bgAnim = fp  

 def setMixing(self, idxs):
  log("mix called idx: " + str(idxs))
  self.mixCol = tuple(map(lambda x: int(255*x), colorsys.hsv_to_rgb(100./random.randint(50,100), 1, .15)))
  self.mixingIdxs = idxs

 def stopMixing(self):
  log("stop mixing called")
  self.mixingIdxs = None
  
 
 def getAlertIdxs(self):
  return [9]

 def thread_loop(self):
  log("threadloop")
  frame=-1
  while True:
   while False and not self.device:
    self.connect()
    if not self.device:
     time.sleep(1)

   frame +=1 
   self.bgAnim(self.colors, frame)
   if self.mixingIdxs:
    mixAnim(self.colors, self.mixCol, frame, self.mixingIdxs)
   
   alertAnim(self.colors, frame , self.getAlertIdxs())

   adjBrightness(self.colors, b = float(self.configMap['brightness']))
   self.serWrite()
   
   frame %= int(self.configMap['nbrBottles'])*30
   if not frame:
     self.setBgAnim(random.choice(self.bgAnimFuncs))
#     self.sync()
     log("animation chage: " + str(self.bgAnim.__module__))

   #time.sleep(1./float(self.configMap["speed"]))
   time.sleep(.001)
  
  
 def setColor(self, idx, r, g, b):
  if idx < 0 or idx > int(self.configMap['nbrBottles'])-1:
   log("Wrong index: " + str(idx))
   return
  if checkColor(r) and checkColor(g) and checkColor(b):
   self.colors[idx] = (r,g,b)
  else:
   log("bad color: r " +str(r) + " g " + str(g) + " b " + str(b))

  
 def connect(self):
  log("connect attempt")
  ports = glob.glob('/dev/ttyUSB*')
  self.ser = serial.Serial(timeout=.01,baudrate=9600)
  for device in ports:
   log("trying: " + str(device))
   self.ser.port = device
   try:
    self.ser.open()
   except:
    log("could not open device" + str(device))
    continue
   self.sync()
   self.ser.write(b'HELL')
   start = time.time()
   result = self.ser.read_all()
   log("got back: "  + str(result))
   if result.find(b'FIRE'):
    self.device = device 
    log("connected to " + str(device))
    return

  log("no device found which answered correct")
  self.device = None
 
 def sync(self):
  pass
#  while self.ser.read(1) != b'1':
#   self.ser.write(b'0')
 
 def serWrite(self):
  for k in self.colors:
#   print(self.colors)
#   log("sending: " + ' '.join(str(hex(e)) for e in bytearray([k, self.colors[k][0],self.colors[k][1],self.colors[k][2]])))
   try:
    #adjust for protocol
    for k,v in self.colors.items():
        self.colors[k] = tuple((val if val < 255 else 254 for val in v))
        self.ser.write(bytearray([0xff, k, self.colors[k][0],self.colors[k][1],self.colors[k][2]]))
#        time.sleep(.01)
        print([int(e)for e in bytearray([0xff, k, self.colors[k][0],self.colors[k][1],self.colors[k][2]])])
   except:
#    pass
    self.device = None
#   print([hex(e) for e in self.ser.read_all()])
  
 def readConfig(self):
  self.configMap = {}
  lines = open("enlightment/config").readlines()
  lines = filter(lambda l: False == l.startswith("#"), lines)
  for l in lines: 
   l = l.strip()
   if l:
    sp = l.split("=")
    sp = [e.strip() for e in sp]
    self.configMap[sp[0]] = sp[1]




if __name__ == "__main__":
 e = Enlightment()
 while True: 
  time.sleep(5)




