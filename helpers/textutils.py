import numpy as np


def getCharBitmap(char):
    file_path = "resources/sprites/letters.npy"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?:.><="
    char = char.upper()
    if char not in letters:
        return np.zeros((5, 3), dtype=np.bool)

    return np.load(file_path)[letters.index(char)]


def getTextBitmap(text):
    out = np.zeros((5, 4*len(text) - 1), np.bool)
    for i, char in enumerate(text):
        out[:, i*4:i*4+3] = getCharBitmap(char)
    return out
