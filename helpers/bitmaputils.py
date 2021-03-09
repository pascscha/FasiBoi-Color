def applyBitmap(bmp, display, loc, bg_color=None, fg_color=(255, 255, 255)):
    """Applies a bitmap to a display. Cuts away any parts that are out of bounds for the display

    Args:
        bmp (2D boolean array): The bitmap to apply
        display (IO.core.Display): The display to apply the bitmap to 
        loc ((int, int)): The top left coordinates where the bitmap should be applied
        color0 ((int, int, int), optional): The color of the background. Defaults to None, which leaves it transparent
        color1 ((int, int, int), optional): The color of the foreground. Defaults to (255, 255, 255). None would leave it transparent.
    """
    for x in range(bmp.shape[1]):
        for y in range(bmp.shape[0]):
            color = fg_color if bmp[y][x] else bg_color
            if color is not None:
                try:
                    display.update(loc[0] + x, loc[1] + y, color)
                except ValueError:
                    pass