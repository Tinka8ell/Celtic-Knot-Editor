# !/usr/bin/python3
# utils.py

try:
    # noinspection PyUnresolvedReferences
    from enums import *
    local = True
except ModuleNotFoundError as e:
    local = False
if local:
    pass
else:
    from Editor.enums import *

from tkinter import *
from tkinter import messagebox


def KnotError(errorText, title="Knot Editor - Oops!"):
    return messagebox.showerror(title, errorText)


def KnotInfo(infoText, title="Knot Editor Help"):
    return messagebox.showinfo(title, infoText)


def KnotConfirm(questionText, title="Oops!"):
    return messagebox.askyesno("Knot Editor - Are you sure?", questionText)


def ligatures2unicode(ligatures):
    # convert groups of 4 ligatures (trailing ones set to blocked) to unicode
    upper = ligatures.upper() + "OOOO"  # allow for empty string
    unicode = ""
    for i in range(0, len(ligatures), 4):
        n = upper[i+0]
        e = upper[i+1]
        s = upper[i+2]
        w = upper[i+3]
        offset = 0
        offset += Ligature[n].value
        offset *= 5
        offset += Ligature[e].value
        offset *= 5
        offset += Ligature[s].value
        offset *= 5
        offset += Ligature[w].value
        unicode += chr(0xE100 + offset)
    if ligatures == "iiii":
        # one special at the moment - platted I:
        unicode = chr(0xE03F)
    return unicode


def unicode2ligatures(unicode):
    # convert unicode to groups of 4 ligatures
    ligatures = ""
    for ch in unicode:
        i = ord(ch)
        if i >= 0xE100:
            # upper private area
            i -= 0xE100
            w = i % 5
            i //= 5
            s = i % 5
            i //= 5
            e = i % 5
            i //= 5
            n = i % 5
            ligatures += int2ligature(n)
            ligatures += int2ligature(e)
            ligatures += int2ligature(s)
            ligatures += int2ligature(w)
        else:
            if i == 0xE03F:
                ligatures = "iiii"  # special platted version
            else:
                ligatures = ""  # not supported! - should this be an exception?
    return ligatures


def int2ligature(i):
    # convert doorway integer to ligature
    d = Doorway(i)
    l = Ligature(d)
    return l.name


def ligature2doorway(ch):
    # convert to ligature doorway
    l = Ligature[ch]
    return l.value


if __name__ == "__main__":
    l = "OXIH"
    a = ligatures2unicode(l)
    print("test:", l, "->", a, "?", l == unicode2ligatures(a))
