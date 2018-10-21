import colorsys, time
def anim(colors, frame):
    stretch = 25
    hueStep = 1/stretch


    bottom(colors,frame, hueStep)
    up(colors,frame, hueStep)
 

def bottom(colors, frame, hueStep):
    for i in range(4):
        h = (i+frame)*hueStep
        colors[i] = convColor(colorsys.hsv_to_rgb(h,1,1))
        colors[7-i] = convColor(colorsys.hsv_to_rgb(h,1,1))

def up(colors, frame, hueStep):
    for i in range(8,11):
        h = (i+frame-8)*hueStep
        colors[i] = convColor(colorsys.hsv_to_rgb(h,1,1))
        colors[14-i+8] = convColor(colorsys.hsv_to_rgb(h,1,1))


def convColor(c):
    t = tuple(map(lambda x: int(255*x), c))
    t = tuple(map(lambda x: x if x else 1, t))
    return t
