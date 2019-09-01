# !/usr/bin/python3
# knot.py

try:
   from enums import *
   local = True
except ModuleNotFoundError as e:
   local = False
if local:
   from utils import *
   # noinspection PyUnresolvedReferences
   from cell import Cell
else:
   from Editor.enums import *
   from Editor.utils import *
   from Editor.cell import Cell


class Knot:

   def __init__(self, width, height):
      self.width = width
      self.height = height
      self.cells = []
      self.symmetry = Symmetry.No
      for y in range(height):
         row = []
         for x in range(width):
            row.append(Cell(x, y))
         self.cells.append(row)
      self.linkCells()
      return
   
   def isValidX(self, x):
      if x < 0:
         return False
      if x > (self.width - 1):
         return False
      return True
   
   def isValidY(self, y):
      if y < 0:
         return False
      if y > (self.height - 1):
         return False
      return True
   
   def linkCells(self):
      # setting neightbours - used by change wall
      for y in range(self.height):
         for x in range(self.width):
            cell = self.cell(x, y)
            if self.isValidY(y - 1):
               cell.setNeighbour(Direction.North, self.cell(x, y - 1))
            else:
               cell.setNeighbour(Direction.North, None)
            if self.isValidX(x + 1):
               cell.setNeighbour(Direction.East, self.cell(x + 1, y))
            else:
               cell.setNeighbour(Direction.East, None)
            if self.isValidY(y + 1):
               cell.setNeighbour(Direction.South, self.cell(x, y + 1))
            else:
               cell.setNeighbour(Direction.South, None)
            if self.isValidX(x - 1):
               cell.setNeighbour(Direction.West, self.cell(x - 1, y))
            else:
               cell.setNeighbour(Direction.West, None)
      # setting symmetry cells - used by change wall if symmetry activated
      for y in range(self.height):
         for x in range(self.width):
            cell = self.cell(x, y)
            xmirror = self.width - x - 1
            ymirror = self.height - y - 1
            ### print("For", x, y, "Mirror", xmirror, ymirror)
            # mirrors always are ok
            ### print("   Horizontal", xmirror, y)
            cell.setSymmetry(Symmetry.Horizontal, self.cell(xmirror, y))
            ### print("   Vertical", x, ymirror)
            cell.setSymmetry(Symmetry.Vertical, self.cell(x, ymirror))
            # 2-way rotation is ok
            ### print("   Rotate180", xmirror, ymirror)
            cell.setSymmetry(Symmetry.Rotate180, self.cell(xmirror, ymirror))
            # 4-way rotations, only vallid if width == height
            if self.width == self.height:
               ### print("   Rotate90", ymirror, x)
               cell.setSymmetry(Symmetry.Rotate90, self.cell(ymirror, x))
               ### print("   Rotate270", y, xmirror)
               cell.setSymmetry(Symmetry.Rotate270, self.cell(y, xmirror))
      return

   def cell(self, x: int, y: int) -> Cell:
      """
      Validate that x and y are in the knot, and then return the relevant Cell
      :param x: coordinate
      :param y: coordinate
      :return: Cell at (x,y)
      """
      if self.width > x >= 0:
         if self.height > y >= 0:
            return self.cells[y][x]
         else:
            raise Exception("More rows than allowed: cell(" + str(x) + "," + str(y) + ")")
      else:
         raise Exception("Line longer than allowed row: cell(" + str(x) + "," + str(y) + ")")

   def print(self) -> str:
      """
      Print the knot as unicode
      Used to see the knot in debug, or display in textbox
      :return: the knot as unicode
      """
      code = ""
      for y in range(self.height):
         for x in range(self.width):
            code += self.cell(x, y).print()
         code += "\n"
      return code

   def show(self) -> str:
      """
      Show the knot as ligatures
      Used the serialise the knot for load and save
      :return: the knot as ligatures
      """
      code = ""
      for y in range(self.height):
         for x in range(self.width):
            code += self.cell(x, y).show()
         code += "\n"
      return code

   def set(self, ligatures: str):
      x = 0
      y = 0
      ligs = ""
      for ch in ligatures:
         if ch == "\n":
            # end of line start new row
            if ligs != "":
               # add last cell
               try:
                  self.cell(x, y).setWalls(ligs)
               except Exception as exc:
                  raise Exception(str(exc) + ' - "' + ligs + '"')
            ligs = ""
            x = 0
            y += 1
         else:
            try:
               # use enum exception to validate ligature
               # noinspection PyUnusedLocal
               test = Ligature[ch]
               ligs += ch
            except KeyError:
               raise Exception("Invalid character ('" + ch + "') in cell(" + str(x) + "," + str(y) + ')'
                               ' - "' + ligs + ch + '"')
            if len(ligs) == 4:
               try:
                  self.cell(x, y).setWalls(ligs)
               except Exception as exc:
                  raise Exception(str(exc) + ' - "' + ligs + '"')
               ligs = ""
               x += 1
      return

   def add(self, new: Symmetry):
      if new & Symmetry.Rotate90:
         self.remove(Symmetry.Rotate180)  # exclusive 90 & 180
      if new & Symmetry.Rotate180:
         self.remove(Symmetry.Rotate90)   # exclusive 90 & 180
      self.symmetry |= new
      return

   def remove(self, old: Symmetry):
      self.symmetry &= ~old
      return

   @staticmethod
   def load(ligatures: str) -> 'Knot':
      width = 0
      height = 0
      x = 0
      ligs = 0
      for ch in ligatures:
         if ch == "\n":
            # end of line start new row
            if ligs > 0:
               # count last cell
               x += 1
            width = max(width, x)
            x = 0
            height += 1
         else:
            ligs += 1
            if ligs == 4:
               ligs = 0
               x += 1
      # end of ligatures
      if ligs > 0:
         # count last cell
         x += 1
      width = max(width, x)
      if x > 0:
         # count last row
         height += 1
      new = Knot(width, height)
      new.set(ligatures)
      return new


if __name__ == "__main__":
   knot = Knot.load("oxxooxxxooxx\nxxxoxxxxxoxx\nxxxoxxxxxoxx\nxxooxxoxxoox")
   print("Knot show:")
   print(knot.show())
   print("Knot print:")
   print(knot.print())
   knot.cell(1, 1).changeWall(Direction.North, Doorway.blocked, Symmetry.No)
   print("Knot show:")
   print(knot.show())
   print("Knot print:")
   print(knot.print())
   knot.cell(1, 1).changeWall(Direction.East, Doorway.head, Symmetry.No)
   print("Knot show:")
   print(knot.show())
   print("Knot print:")
   print(knot.print())
   knotCode = '''oooooooooxxoooxx
oxxooxixxxxxxoox
xixoIIIIxoxi
xxooixoxxxxxooxxoooooxxoooxx
ooooooooxxooxxxxoxixxxxxxoox
ooooooooooooxixoIIIIxoxioooo'''
   knot = Knot.load(knotCode)
   print("Knot show:")
   print(knot.show())
   print("Knot print:")
   print(knot.print())
