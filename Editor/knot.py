# !/usr/bin/python3
# knot.py

from enums import *
from utils import *
from cell import Cell

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
            cell = self.cell(x,y)
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
            cell = self.cell(x,y)
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

   def cell(self, x, y):
      if x < self.width and x >= 0:
         if y < self.height and y >= 0:
            return self.cells[y][x]
         else:
            raise Exception("More rows than allowed: cell(" + str(x) + "," + str(y) + ")")
      else:
         raise Exception("Line longer than allowed row: cell(" + str(x) + "," + str(y) + ")")


   def print(self):
      # print the knot as unicode
      # used to see the knot in debug, or display in textbox
      knotCode = ""
      for y in range(self.height):
         for x in range(self.width):
            knotCode += self.cell(x, y).print()
         knotCode += "\n"
      return knotCode

   def show(self):
      # show the knot as ligatures
      # used the serialise the knot for load and save
      knotCode = ""
      for y in range(self.height):
         for x in range(self.width):
            knotCode += self.cell(x, y).show()
         knotCode += "\n"
      return knotCode

   def set(self, ligatures):
      upper = ligatures.upper()
      x = 0
      y = 0
      l = ""
      for ch in upper:
         if ch == "\n":
            # end of line start new row
            if l != "":
               # add last cell
               try:
                  self.cell(x, y).setWalls(l)
               except Exception as e:
                  raise Exception(str(e) + ' - "' + l + '"')
            l = ""
            x = 0
            y += 1
         else:
            try:
               test = Ligature[ch]
               l += ch
            except:
               raise Exception("Invalid character ('" + ch + "') in cell(" + str(x) + "," + str(y) + ') - "' + l + ch + '"')
            if len(l) == 4:
               try:
                  self.cell(x, y).setWalls(l)
               except Exception as e:
                  raise Exception(str(e) + ' - "' + l + '"')
               l = ""
               x += 1
      return

   def load(ligatures):
      width = 0
      height = 0
      x = 0
      l = 0
      for ch in ligatures:
         if ch == "\n":
            # end of line start new row
            if l > 0:
               # count last cell
               x += 1
            width = max(width, x)
            x = 0
            height += 1
         else:
            l += 1
            if l == 4:
               l = 0
               x += 1
      # end of ligatures
      if l > 0:
         # count last cell
         x += 1
      width = max(width, x)
      if x > 0:
         # count last row
         height += 1
      knot = Knot(width, height)
      knot.set(ligatures)
      return knot

   def addSymmetry(self, newSymmetry):
      if newSymmetry & Symmetry.Rotate90:
         self.remove(Symmetry.Rotate180) # exclusive 90 & 180
      if newSymmetry & Symmetry.Rotate180:
         self.remove(Symmetry.Rotate90) # exclusive 90 & 180
      self.symmetry |= newSymmetry
      return

   def removeSymmetry(self, oldSymmetry):
      self.symmetry &= ~oldSymmetry
      return

   def expand(self, newWidth, newHeight):
      print("Expand called with old:", self.width, ",", self.height, "- new:", newWidth, ",", newHeight)
      return


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
   map = '''oooooooooxxoooxx
oxxooxixxxxxxoox
xixoIIIIxoxi
xxooixoxxxxxooxxoooooxxoooxx
ooooooooxxooxxxxoxixxxxxxoox
ooooooooooooxixoIIIIxoxioooo'''
   knot = Knot.load(map)
   print("Knot show:")
   print(knot.show())
   print("Knot print:")
   print(knot.print())

