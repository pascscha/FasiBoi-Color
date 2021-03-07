import numpy as np

def getCharBitmap(char):
    file_path = "resources/sprites/letters.npy"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?:.><="
    char = char.upper()
    if char not in letters:
        return np.zeros((5,3), dtype=np.bool)

    return np.load(file_path)[letters.index(char)]

def getTextBitmap(text):
    out = np.zeros((5, 4*len(text) - 1), np.bool)
    for i, char in enumerate(text):
        out[:,i*4:i*4+3] = getCharBitmap(char)
    return out
        
def applyBitmap(bmp, display, loc, color0=None, color1=(255, 255, 255)):
    for x in range(bmp.shape[1]):
        for y in range(bmp.shape[0]):
            color = color1 if bmp[y][x] else color0
            if color is not None:
                try:
                    display.update(loc[0] + x, loc[1] + y, color)
                except ValueError:
                    pass