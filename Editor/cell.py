# !/usr/bin/python3
# knot.py
from typing import Dict, TypeVar

try:
   # noinspection PyUnresolvedReferences
   from enums import Direction, Symmetry
   local = True
except ModuleNotFoundError as e:
   local = False
if local:
   from utils import *
else:
   from Editor.enums import Direction, Symmetry
   from Editor.utils import *


class Cell:

   wall = TypeVar('wall', Doorway, type(None))
   walls: Dict[Direction, wall]
   cell = TypeVar('cell', 'Cell', type(None))
   neighbours: Dict[Direction, cell]
   symmetries: Dict[Symmetry, cell]

   def __init__(self, x, y):
      self.x = x
      self.y = y
      self.walls = {Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None}
      self.neighbours = {Direction.North: None, Direction.East: None, Direction.South: None, Direction.West: None}
      self.symmetries = {Symmetry.Horizontal: None,
                         Symmetry.Vertical: None,
                         Symmetry.Rotate90: None,
                         Symmetry.Rotate180: None,
                         Symmetry.Rotate270: None}
      return

   def setNeighbour(self, direction: Direction, cell: cell) -> None:
      self.neighbours[direction] = cell
      return
   
   def setSymmetry(self, symmetry: Symmetry, cell: 'Cell') -> None:
      self.symmetries[symmetry] = cell
      return

   def neighbour(self, direction: Direction) -> 'Cell':
      return self.neighbours[direction]

   def symmetry(self, symmetry: Symmetry) -> 'Cell':
      return self.symmetries[symmetry]

   def wall(self, direction: Direction) -> Doorway:
      wall = self.walls[direction]
      if not wall:
         wall = Doorway.blocked
      return wall

   def setWall(self, direction: Direction, wall: Doorway) -> None:
      self.walls[direction] = wall
      return

   def setWalls(self, ligatures: str) -> None:
      if not ligatures or ligatures == "":
         ligatures = "OOOO"
      else:
         ligatures += "OOO"
      self.setWall(Direction.North, ligature2doorway(ligatures[0]))
      self.setWall(Direction.East, ligature2doorway(ligatures[1]))
      self.setWall(Direction.South, ligature2doorway(ligatures[2]))
      self.setWall(Direction.West, ligature2doorway(ligatures[3]))
      return

   def isEmpty(self) -> bool:
      """
      Test if only blocked or remove on all walls
      :return: True iff all walls blocked or removed
      """
      isEmpty = True
      for direction in Direction:
         isEmpty = isEmpty and (self.wall(direction) == Doorway.blocked or self.wall(direction) == Doorway.removed)
      return isEmpty

   def changeWall(self, direction: Direction, wall: Doorway, symmetries: Symmetry) -> None:
      current = self.walls[direction]
      if not current:
         current = Doorway.blocked
      ### print("Calling changeWall:", self.x, self.y, direction.name, wall.name + ": current = ", current.name)
      if current != wall:
         # has changed, so change related walls
         ### print("Changing:", self.x, self.y, "changeWall(", direction.name + ",", wall.name + ", symmetries):
         ### current = ", current.name)
         self.setWall(direction, wall)
         neighbour = self.neighbour(direction)
         if neighbour:
            oppositeWall = wall.opposite
            oppositeDirection = direction.opposite
            ### print("set neighbour", neighbour.x, neighbour.y, oppositeDirection.name, oppositeWall.name)
            neighbour.setWall(oppositeDirection, oppositeWall)
         ### print("Checking symmetry:")
         ### print((symmetries & Symmetry.Horizontal))
         if symmetries & Symmetry.Horizontal:
            paired = self.symmetry(Symmetry.Horizontal)
            if direction == Direction.East or direction == Direction.West:
               oppositeDirection = direction.opposite
            else:
               oppositeDirection = direction  # horizontal reflection does not effect vertical facing walls
            ### print("paired:", paired.x, paired.y, Symmetry.Horizontal.name)
            # do neighbours, but not symmetries (to avoid infinite recursion)
            paired.changeWall(oppositeDirection, wall, Symmetry.No)
         ### print((symmetries & Symmetry.Vertical))
         if symmetries & Symmetry.Vertical:
            paired = self.symmetry(Symmetry.Vertical)
            if direction == Direction.North or direction == Direction.South:
               oppositeDirection = direction.opposite
            else:
               oppositeDirection = direction  # horizontal reflection does not effect horizontal facing walls
            ### print("paired:", paired.x, paired.y, Symmetry.Vertical.name)
            # do neighbours, but not symmetries (to avoid infinite recursion)
            paired.changeWall(oppositeDirection, wall, Symmetry.No)
         ### print((symmetries & Symmetry.Rotate180), "or", (symmetries & Symmetry.Rotate90))
         if (symmetries & Symmetry.Rotate180) or (symmetries & Symmetry.Rotate90) or \
                 ((symmetries & Symmetry.Horizontal) and (symmetries & Symmetry.Vertical)):
            # 90 maps 180 as well as 90 and 270 below, and Horizontal and Vertical together also hits 180 ...
            paired = self.symmetry(Symmetry.Rotate180)
            oppositeDirection = direction.opposite
            ### print("paired:", paired.x, paired.y, Symmetry.Rotate180.name, "or", Symmetry.Rotate90.name)
            # do neighbours, but not symmetries (to avoid infinite recursion)
            paired.changeWall(oppositeDirection, wall, Symmetry.No)
         ### print((symmetries & Symmetry.Rotate90))
         if symmetries & Symmetry.Rotate90:
            paired = self.symmetry(Symmetry.Rotate90)
            if paired:
               rotatedDirection = direction.cw
               ### print("paired:", paired.x, paired.y, Symmetry.Rotate90.name)
               # do neighbours, but not symmetries (to avoid infinite recursion)
               paired.changeWall(rotatedDirection, wall, Symmetry.No)
            paired = self.symmetry(Symmetry.Rotate270)
            if paired:
               rotatedDirection = direction.ccw
               ### print("paired:", paired.x, paired.y, Symmetry.Rotate270.name)
               # do neighbours, but not symmetries (to avoid infinite recursion)
               paired.changeWall(rotatedDirection, wall, Symmetry.No)
         ### print("End symmetry check")
      return

   def print(self) -> str:
      """
      Print the cell as unicode
      Used to see the cell in debug, or display in textbox
      :return: the cell as unicode
      """
      knotCode = self.show()
      return ligatures2unicode(knotCode)

   def show(self) -> str:
      """
      Show the cell as ligatures
      Used the serialise the cell for load and save
      :return: the cell as ligatures
      """
      knotCode = Ligature(self.wall(Direction.North)).name
      knotCode += Ligature(self.wall(Direction.East)).name
      knotCode += Ligature(self.wall(Direction.South)).name
      knotCode += Ligature(self.wall(Direction.West)).name
      return knotCode


if __name__ == "__main__":
   pass  # no test code
