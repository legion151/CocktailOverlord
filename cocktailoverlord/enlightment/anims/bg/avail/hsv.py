import colorsys
def anim(colors, frame):
 n = len(colors)
 stretch = 20
 frame %= (n*stretch)
 hue = 1.0/(n*stretch)*frame
 for k,v in colors.items():
  colors[k] = tuple(map(lambda x: int(255*x), colorsys.hsv_to_rgb(hue, 1.0, 1.0)))


