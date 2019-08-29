# !/usr/bin/python3
# knot.py

from enums import *
from utils import *

class Cell:

   def __init__(self, x, y):
      self.x = x
      self.y = y
      self.walls = {Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None}
      self.neighbours = {Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None}
      self.symmetries = {Symmetry.Horizontal: None, Symmetry.Vertical: None, Symmetry.Rotate90: None, Symmetry.Rotate180: None, Symmetry.Rotate270: None, }
      return

   def setNeighbour(self, direction, cell):
      self.neighbours[direction] = cell
      return
   
   def setSymmetry(self, symmetry, cell):
      self.symmetries[symmetry] = cell
      return

   def neighbour(self, direction):
      return self.neighbours[direction]

   def symmetry(self, symmetry):
      return self.symmetries[symmetry]

   def wall(self, direction):
      wall = self.walls[direction]
      if not wall:
         wall = Doorway.blocked
      return wall

   def setWall(self, direction, wall):
      self.walls[direction] = wall
      return

   def setWalls(self, ligatures):
      if not ligatures or ligatures == "":
         upper = "OOOO"
      else:
         upper = ligatures.upper() + "OOO"
      self.setWall(Direction.North, ligature2doorway(upper[0]))
      self.setWall(Direction.East, ligature2doorway(upper[1]))
      self.setWall(Direction.South, ligature2doorway(upper[2]))
      self.setWall(Direction.West, ligature2doorway(upper[3]))
      return

   def empty(self): # test if only blocked or remove on all walls
      empty = True
      for d in Direction:
         empty = empty and (self.wall(d) == Doorway.blocked or self.wall(d) == Doorway.removed)
      return empty

   def changeWall(self, direction, wall, symmetries):
      current = self.walls[direction]
      if not current:
         current = Doorway.blocked
      ### print("Calling changeWall:", self.x, self.y, direction.name, wall.name + ": current = ", current.name)
      if current != wall:
         # has changed, so change related walls
         ### print("Changing:", self.x, self.y, "changeWall(", direction.name + ",", wall.name + ", symmetries): current = ", current.name)
         self.setWall(direction, wall)
         neighbour = self.neighbour(direction)
         if neighbour:
            oppositeWall = Opposite(wall)
            oppositeDirection = Opposite(direction)
            ### print("set neighbour", neighbour.x, neighbour.y, oppositeDirection.name, oppositeWall.name)
            neighbour.setWall(oppositeDirection, oppositeWall)
         ### print("Checking symmetry:")
         ### print((symmetries & Symmetry.Horizontal))
         if (symmetries & Symmetry.Horizontal):
            paired = self.symmetry(Symmetry.Horizontal)
            if (direction == Direction.East or direction == Direction.West):
               oppositeDirection = Opposite(direction)
            else:
               oppositeDirection = direction # horizontal reflection does not effect vertical facing walls
            ### print("paired:", paired.x, paired.y, Symmetry.Horizontal.name)
            paired.changeWall(oppositeDirection, wall, Symmetry.No) # do neighbours, but not symmetries (to avoid infinite recursion)
         ### print((symmetries & Symmetry.Vertical))
         if (symmetries & Symmetry.Vertical):
            paired = self.symmetry(Symmetry.Vertical)
            if (direction == Direction.North or direction == Direction.South):
               oppositeDirection = Opposite(direction)
            else:
               oppositeDirection = direction # horizontal reflection does not effect horizontal facing walls
            ### print("paired:", paired.x, paired.y, Symmetry.Vertical.name)
            paired.changeWall(oppositeDirection, wall, Symmetry.No) # do neighbours, but not symmetries (to avoid infinite recursion)
         ### print((symmetries & Symmetry.Rotate180), "or", (symmetries & Symmetry.Rotate90))
         if (symmetries & Symmetry.Rotate180) or (symmetries & Symmetry.Rotate90) or ((symmetries & Symmetry.Horizontal) and (symmetries & Symmetry.Vertical)):
            # 90 maps 180 as well as 90 and 270 below, and Horizontal and Vertical together also hits 180 ...
            paired = self.symmetry(Symmetry.Rotate180)
            oppositeDirection = Opposite(direction)
            ### print("paired:", paired.x, paired.y, Symmetry.Rotate180.name, "or", Symmetry.Rotate90.name)
            paired.changeWall(oppositeDirection, wall, Symmetry.No) # do neighbours, but not symmetries (to avoid infinite recursion)
         ### print((symmetries & Symmetry.Rotate90))
         if (symmetries & Symmetry.Rotate90):
            paired = self.symmetry(Symmetry.Rotate90)
            if paired:
               rotatedDirection = Rotated(direction)
               ### print("paired:", paired.x, paired.y, Symmetry.Rotate90.name)
               paired.changeWall(rotatedDirection, wall, Symmetry.No) # do neighbours, but not symmetries (to avoid infinite recursion)
            paired = self.symmetry(Symmetry.Rotate270)
            if paired:
               rotatedDirection = Opposite(Rotated(direction))
               ### print("paired:", paired.x, paired.y, Symmetry.Rotate270.name)
               paired.changeWall(rotatedDirection, wall, Symmetry.No) # do neighbours, but not symmetries (to avoid infinite recursion)
         ### print("End symmetry check")
      return

   def print(self):
      # print the cell as unicode
      # used to see the cell in debug, or display in textbox
      knotCode = self.show()
      return ligatures2unicode(knotCode)

   def show(self):
      # show the cell as ligatures
      # used the serialise the cell for load and save
      knotCode = Ligature(self.wall(Direction.North)).name
      knotCode += Ligature(self.wall(Direction.East)).name
      knotCode += Ligature(self.wall(Direction.South)).name
      knotCode += Ligature(self.wall(Direction.West)).name
      return knotCode


if __name__ == "__main__":
   pass # no test code

