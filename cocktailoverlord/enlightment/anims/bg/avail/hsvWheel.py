import colorsys
def anim(colors, frame):
 n = len(colors)
 stretch = 14
 hueFrac = 1.0/(n*stretch)
 
 for idx in range(n):
     hue = hueFrac*(idx+frame)
     colors[idx] = tuple(map(lambda x: int(255*x), colorsys.hsv_to_rgb(hue, 1.0, 1.0)))




