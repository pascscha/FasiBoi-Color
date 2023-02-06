import math
import numpy as np


def cut(img_w, img_h, disp_w, disp_h, x, y):
    img_left = max(0, -x)
    img_top = max(0, -y)
    img_right = min(img_w, disp_w - x)
    img_bottom = min(img_h, disp_h - y)

    dsp_left = max(0, x)
    dsp_top = max(0, y)
    dsp_right = dsp_left + img_right - img_left
    dsp_bottom = dsp_top + img_bottom - img_top

    return (img_left, img_top, img_right, img_bottom), (
        dsp_left,
        dsp_top,
        dsp_right,
        dsp_bottom,
    )


def apply_bitmap(bmp, display, loc, bg_color=None, fg_color=(255, 255, 255)):
    """Applies a bitmap to a display. Cuts away any parts that are out of bounds for the display

    Args:
        bmp (2D boolean array): The bitmap to apply
        display (IO.core.Display): The display to apply the bitmap to
        loc ((int, int)): The top left coordinates where the bitmap should be applied
        bg_color ((int, int, int), optional): The color of the background. Defaults to None, which leaves it transparent
        fg_color ((int, int, int), optional): The color of the foreground. Defaults to (255, 255, 255). None would leave
         it transparent.
    """
    x, y = loc
    h, w = bmp.shape

    (bmp_left, bmp_top, bmp_right, bmp_bottom), (
        dsp_left,
        dsp_top,
        dsp_right,
        dsp_bottom,
    ) = cut(w, h, display.width, display.height, x, y)

    cut_dsp = display.pixels[dsp_left:dsp_right, dsp_top:dsp_bottom]

    cw, ch, _ = cut_dsp.shape
    if cw * ch > 0:
        cut_bmp = bmp.T[bmp_left:bmp_right, bmp_top:bmp_bottom]

        if fg_color is not None:
            cut_dsp[np.where(cut_bmp)] = fg_color
        if bg_color is not None:
            cut_dsp[np.where(1 - cut_bmp)] = bg_color


def apply_image(img, display, loc):
    x, y = loc
    h, w = img.shape[:2]

    (img_left, img_top, img_right, img_bottom), (
        dsp_left,
        dsp_top,
        dsp_right,
        dsp_bottom,
    ) = cut(w, h, display.width, display.height, x, y)

    if (dsp_right - dsp_left) * (dsp_bottom - dsp_top) > 0:
        cut_img = img.transpose(1, 0, 2)[img_left:img_right, img_top:img_bottom]

        if cut_img.shape[2] == 3:
            display.pixels[dsp_left:dsp_right, dsp_top:dsp_bottom] = cut_img
        else:
            display.pixels[dsp_left:dsp_right, dsp_top:dsp_bottom] = cut_img[:, :, :3]


def get_color(image, loc, default=np.array((0, 0, 0))):
    x, y = loc
    if 0 <= x < image.shape[0] and 0 <= y < image.shape[1]:
        return image[x][y]
    else:
        return default


def get_antialiased_color(image, loc):
    x, y = loc

    if int(x) == x:
        x1 = int(x)
        x2 = int(x)
        px1 = 1
        px2 = 0
    else:
        x1 = math.floor(x)
        x2 = math.ceil(x)
        px1 = 1 - abs(x - x1)
        px2 = 1 - abs(x - x2)

    if int(y) == y:
        y1 = int(y)
        y2 = int(y)
        py1 = 1
        py2 = 0
    else:
        y1 = math.floor(y)
        y2 = math.ceil(y)
        py1 = 1 - abs(y - y1)
        py2 = 1 - abs(y - y2)

    return (
        get_color(image, (x1, y1)) * px1 * py1
        + get_color(image, (x1, y2)) * px1 * py2
        + get_color(image, (x2, y1)) * px2 * py1
        + get_color(image, (x2, y2)) * px2 * py2
    ).astype(np.uint8)
