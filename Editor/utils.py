# !/usr/bin/python3
# utils.py

from enums import *

from tkinter import *
from tkinter import messagebox

def KnotError(errorText, title = "Knot Editor - Oops!"):
      return messagebox.showerror(title, errorText)

def KnotInfo(infoText, title = "Knot Editor Help"):
      return messagebox.showinfo(title, infoText)

def KnotConfirm(questionText, title = "Oops!"):
      return messagebox.askyesno("Knot Editor - Are you sure?", questionText)

def ligatures2unicode(ligatures):
   # convert groups of 4 ligatures (trailing ones set to blocked) to unicode
   upper = ligatures.upper() + "OOOO" # allow for empty string
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
      unicode += chr(0xE100 +offset)
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
            ligatures = "iiii" # special platted version
         else:
            ligatures = "" # not supported! - should this be an exception?
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

def Opposite(thing):
   # also acts as rotate direction by 180 degrees
   oppLig = {"O": "O", "I": "I", "X": "X", "H": "B", "B": "H", "o": "o", "i": "i", "x": "x", "h": "b", "b": "h"}
   oppDoor = {Doorway.blocked: Doorway.blocked,
              Doorway.crossed: Doorway.crossed,
              Doorway.straight: Doorway.straight,
              Doorway.head: Doorway.beak,
              Doorway.beak: Doorway.head,
              Doorway.removed: Doorway.removed,
              Doorway.platted: Doorway.platted}
   oppDir = {Direction.North: Direction.South,
             Direction.East: Direction.West,
             Direction.South: Direction.North,
             Direction.West: Direction.East}
   if isinstance(thing, Doorway):
      # print("Opposite Doorway:", thing, oppDoor[thing])
      return oppDoor[thing]
   if isinstance(thing, Direction):
      # print("Opposite Direction:", thing, oppDir[thing])
      return oppDir[thing]
   # print("Opposite Ligature:", thing, oppLig[thing])
   return oppLig[thing]

def Rotated(direction):
   # rotate direction by 90 degrees
   rotated = {Direction.North: Direction.East,
              Direction.East: Direction.South,
              Direction.South: Direction.West,
              Direction.West: Direction.North}
   return rotated[direction]


if __name__ == "__main__":
   l = "OXIH"
   a = ligatures2unicode(l)
   print("test:", l, "->", a, "?", l == unicode2ligatures(a))
   for d in Direction:
      print("Dir:", d.name, "Op:", Opposite(d).name, "Rot:", Rotated(d).name, "Rot:Op:", Rotated(Opposite(d)).name, "either:", Rotated(Opposite(d)) == Opposite(Rotated(d)))
