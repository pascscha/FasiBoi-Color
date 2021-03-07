def applyBitmap(bmp, display, loc, color0=None, color1=(255, 255, 255)):
    for x in range(bmp.shape[1]):
        for y in range(bmp.shape[0]):
            color = color1 if bmp[y][x] else color0
            if color is not None:
                try:
                    display.update(loc[0] + x, loc[1] + y, color)
                except ValueError:
                    pass