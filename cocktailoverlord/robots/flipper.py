#!/usr/bin/python3

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

from robots.robot import Robot

class Flipper(Robot):

    positions = [
        (-187, -2, -188, -170), #  0 l
        (-165, -2, -160, -170), #  1 u
        (-153, -2, -148, -170), #  2 l
        (-135, -2, -125, -170), #  3 u
        (-127, -2, -125, -170), #  4 l
        (-120, -2, -125, -170), #  5 u
        (-100, -2, -102, -170), #  6 l
        ( -90, -2,  -95, -170), #  7 u
        ( -63, -2,  -59, -170), #  8 l
        ( -45, -2,  -40, -170), #  9 u
        ( -36, -2,  -34, -170), # 10 l      
        ( -28, -2,  -33, -170), # 11 u
        ( -10, -2,  -12, -170), # 12 l      
        (  15, -2,   23, -170), # 13 u
        (  30, -2,   35, -170), # 14 l
        
    ]

    for i in range(len(positions)):
        p = positions[i]
        positions[i] = (p[0] - 1.5, p[1], p[2]-1.5, p[3])

    num_ingredients = len(positions)

    def __init__(self, port=None):
        super().__init__(port)
        self.speedx = 10000
        self.speedy = 5000

    def gcode(self, pos, amount, reserve):
        xo,yo, xi, yi = self.positions[pos]
        sx, sy = self.speedx, self.speedy
        time = max(amount / 10. - 0.7, 0.2) # XXX use reserve
        return b"""
g1 y %i f %i
g1 x %i f %i
g1 x %i y %i f %i
g4 P %.2f
g1 x %i y %i f %i
""" % (yo, sy,
       xo, sx,
       xi, yi, sy,
       time,
       xo, yo, sy)

if __name__ == "__main__":
    al = AutoLoader("/dev/ttyUSB0")
    al.send(b'\n$H\n')
    #for i in (0, 1, 2, 14,):
    #    al.send(al.gcode(i, 2.5))
    #print(al.gcode(9, 2.5))
    al.wait()
