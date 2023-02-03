import numpy as np

letter_bmps = list(np.load("resources/sprites/letters.npy"))

def get_char_bitmap(char, monospace=True):
    """Gets the bitmap for a single char

    Args:
        char (chr): The character to get the bitmap from

    Returns:
        2D boolean array: A 3x5 bitmap representing the given character
    """
    global letter_bmps

    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
    char = char.upper()
    if char not in letters:
        return np.zeros((5, 3), dtype=np.uint8)

    bmp = letter_bmps[letters.index(char)]
    if not monospace:
        while np.all(bmp[:,0]==False):
            bmp = bmp[:,1:]

        while np.all(bmp[:,-1]==False):
            bmp = bmp[:,:-1]    

    return bmp
        


bmp_memory = {}
def get_text_bitmap(text, monospace=True):
    """Gets a bitmap of a string. Distance between two characters is 1 pixel

    Args:
        text (str): The string to convert to a bitmap

    Returns:
        2D boolean array: A bitmap representing the given string
    """
    global bmp_memory
    if (text, monospace) in bmp_memory:
        return bmp_memory[(text, monospace)]

    bmps = [get_char_bitmap(char, monospace=monospace) for char in text]
    width = len(bmps) - 1 + sum([bmp.shape[1] for bmp in bmps])
    height = 5

    out = np.zeros((height, width), np.uint8)
    x = 0
    for bmp in bmps:
        out [:, x:x+bmp.shape[1]] = bmp
        x += bmp.shape[1] + 1

    bmp_memory[(text, monospace)] = out
    return out
