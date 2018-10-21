import colorsys, time
def anim(colors, frame):
 n = len(colors)
 stretch = 1 
 for k in range(0, int(n/2)):
    hue = 1.0/(n*stretch)*(frame+k)
    colors[k] = tuple( map(lambda x: int(255*x),  colorsys.hsv_to_rgb(hue, 1.0, 1.0)) )
    colors[n-1-k] = tuple( map(lambda x: int(255*x),  colorsys.hsv_to_rgb(hue, 1.0, 1.0)) )


