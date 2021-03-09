import numpy as np

def getCharBitmap(char):
    """Gets the bitmap for a single char

    Args:
        char (chr): The character to get the bitmap from

    Returns:
        2D boolean array: A 3x5 bitmap representing the given character
    """
    file_path = "resources/sprites/letters.npy"
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!?:.><="
    char = char.upper()
    if char not in letters:
        return np.zeros((5, 3), dtype=np.bool)

    return np.load(file_path)[letters.index(char)]


def getTextBitmap(text):
    """Gets a bitmap of a string. Distance between two characters is 1 pixel

    Args:
        text (str): The string to convert to a bitmap

    Returns:
        2D boolean array: A bitmap representing the given string
    """
    out = np.zeros((5, 4*len(text) - 1), np.bool)
    for i, char in enumerate(text):
        out[:, i*4:i*4+3] = getCharBitmap(char)
    return out
