def anim(colors, frame):
    j = int(frame/15) %256

    for i in range(15):
        Wheel(colors, i,(int(i * 256 / 15) + j) & 255)

def Wheel(colors, i, WheelPos):
  if (WheelPos < 85):
    colors[i]=(WheelPos * 3, 255 - WheelPos * 3, 0)
  elif (WheelPos < 170):
    WheelPos -= 85;
    colors[i]=(255 - WheelPos * 3, 0, WheelPos * 3)
  else:
    WheelPos -= 170;
    colors[i]=(0, WheelPos * 3, 255 - WheelPos * 3)


