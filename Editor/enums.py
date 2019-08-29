# !/usr/bin/python3
# enums.py

from enum import Enum, IntEnum, Flag, auto

# Decorator classes:

'''
Add the opposite attribute using the mapping of enum names
'''
class Reverse:
   def __init__(self, reverse_map):
      self.reverse_map = reverse_map

   def __call__(self, enum):
      # use the match pairs in reverse_map to link enum names that are opposited of each other
      for fwd, rev in self.reverse_map.items():
         enum[fwd].opposite = enum[rev]
         enum[rev].opposite = enum[fwd]
      return enum

'''
Add the cw (clockwise) and ccw (counter clockwise) attributes using the mapping of enum names
'''
class Rotate:
   def __init__(self, rotate_map):
      self.rotate_map = rotate_map

   def __call__(self, enum):
      # each mapping is of clockwise links, so reverse mapping gives counter clockwise
      for fwd, rot in self.rotate_map.items():
         enum[fwd].cw = enum[rot]
         enum[rot].ccw = enum[fwd]
      return enum

# as decorators are for different attribute we can apply one on top of the other and add both sets of attributes
@Reverse( {'North': 'South', 'East': 'West'} )
@Rotate( {'North': 'East', 'East': 'South', 'South': 'West', 'West': 'North'} )
class Direction(IntEnum):
   # is an integer and an Enum!
   North = 0
   East = 1
   South = 2
   West = 3

class Doorway(IntEnum):
   # is an integer and an Enum!
   blocked = 0
   crossed = 1
   straight = 2
   head = 3
   beak = 4
   removed = blocked + 5 # if only combined with "straight" removes line from that side
   # note that int value 6 has no Doorway defined, so not all int values in the range are valid
   platted = straight + 5 # if all "platted" then do plat alternative, if only combined with "blocked" will remove line from that side

class Ligature(Enum):
   O = Doorway.blocked
   X = Doorway.crossed
   I = Doorway.straight
   H = Doorway.head
   B = Doorway.beak
   # added lowercase versions, so will save uppercasing for some and introduce alternatives
   o = Doorway.removed # if only combined with 'I' and 'i' removes line from that side
   x = Doorway.crossed # for the moment just mapped onto 'X'
   i = Doorway.platted # if all 'i' then do plat alternative, if only combined with 'O' and 'o' will remove line from that side
   h = Doorway.head # for the moment just mapped onto 'H'
   b = Doorway.beak # for the moment just mapped onto 'B'

class Symmetry(Flag):
   No = 0              # base - no symmetry
   Horizontal = auto() # horizontal mirrow
   Vertical   = auto() # vertical mirror
   Rotate90   = auto() # N -> E - 90 rotation - used to indicate 4-way rotation
   Rotate180  = auto() # N -> S - 180 rotation - used to indicate 2-way rotation (also equivalent of Horizontal and Verical!)
   Rotate270  = auto() # N -> W - 270 rotation - not used to indicate symmetry


if __name__ == "__main__":
   print("Direction:")
   for d in Direction:
      print(d, d.cw, d.opposite, d.ccw)
      i = d.value
      print(i, d, d.name, d.value)
      j = Direction(i).value
      print(j, Direction(j), Direction(j).name, Direction(j).value, i == j, Direction.South, Direction(i) == Direction.South)
      n = Direction(i).name
      print(n, Direction[n], Direction[n].name, Direction[n].value, n == Direction[n].name)
   print("max dir =", len(Direction))
   print("Ligature:")
   for l in Ligature:
      print(l, l.name, l.value)
   print("Doorway:")
   for d in Doorway:
      print(d, d.name, d.value)
   max = len(Doorway)
   print("max d =", max)
   print("Symmetry:")
   for s in Symmetry:
      print(s, s.name, s.value)
