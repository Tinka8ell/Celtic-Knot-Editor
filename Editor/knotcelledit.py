# !/usr/bin/python3
# ShowMe.py
from tkinter import *
from tkinter import font
from tkinter import ttk

try:
   # noinspection PyUnresolvedReferences
   from knot import Cell, Direction, Doorway, Ligature, Symmetry
   local = True
except ModuleNotFoundError as e:
   local = False
if local:
   pass
else:
   from Editor.knot import Cell, Direction, Doorway, Symmetry


class KnotCellEdit(Frame):
   def __init__(self, master=None):
      super().__init__(master)
      self.master = master
      self.frame = master
      self.cell = None
      self.callback = None
      self.symmetries = Symmetry.No
      self.create_widgets()

   # noinspection PyAttributeOutsideInit
   def create_widgets(self) -> None:
      """
      Add widgets to frame
      :return:
      """
      master = self
      frame = self.master
      master.grid_columnconfigure(0, weight=1)
      master.grid_rowconfigure(0, weight=1)
      frame.grid_columnconfigure(0, weight=1)
      frame.grid_columnconfigure(1, weight=1)
      frame.grid_columnconfigure(2, weight=1)
      frame.grid_rowconfigure(0, weight=1)
      frame.grid_rowconfigure(1, weight=1)
      frame.grid_rowconfigure(2, weight=1)

      self.font = font.Font(family="KNOTS Zoo", size=72)
      self.view = Label(self.frame, text="O", font=self.font)
      self.view.grid(row=1, column=1, sticky=(N, W, E, S))

      self.doorways = list(Doorway.__members__.keys())
      chars = 0
      for door in self.doorways:
         chars = max(chars, len(door))
      self.northwall = self.addCombo(self.frame, list(self.doorways), chars, 0, 1, self.changeNorthWall)
      self.eastwall = self.addCombo(self.frame, list(self.doorways), chars, 1, 2, self.changeEastWall)
      self.southwall = self.addCombo(self.frame, list(self.doorways), chars, 2, 1, self.changeSouthWall)
      self.westwall = self.addCombo(self.frame, list(self.doorways), chars, 1, 0, self.changeWestWall)
      self.reset()
      return

   @staticmethod
   def addCombo(frame, values, width, row, column, callback):
      combo = ttk.Combobox(frame, values=values, width=width)
      combo.grid(row=row, column=column)
      combo.bind("<<ComboboxSelected>>", callback)
      return combo

   def reset(self):
      self.cell = None
      self.view["text"] = "O"
      self.northwall.current(0)
      self.eastwall.current(0)
      self.southwall.current(0)
      self.westwall.current(0)
      return

   # noinspection PyUnusedLocal
   def changeNorthWall(self, event):
      self.changeWall(Doorway[self.northwall.get()], Direction.North)
      return

   # noinspection PyUnusedLocal
   def changeEastWall(self, event):
      self.changeWall(Doorway[self.eastwall.get()], Direction.East)
      return
        
   # noinspection PyUnusedLocal
   def changeSouthWall(self, event):
      self.changeWall(Doorway[self.southwall.get()], Direction.South)
      return
        
   # noinspection PyUnusedLocal
   def changeWestWall(self, event):
      self.changeWall(Doorway[self.westwall.get()], Direction.West)
      return
        
   def changeWall(self, doorway, direction):
      ### print("cell editor calling change wall:", direction.name, doorway.name)
      if self.cell:
         self.cell.changeWall(direction, doorway, self.symmetries)
         self.show()
         if self.callback:
            self.callback()
      return
    
   def show(self):
      if self.cell:
         text = self.cell.print()
         self.view["text"] = text
      else:
         self.view["text"] = "O"
      return

   def change(self, symmetries):
      self.symmetries = symmetries
      return

   def set(self, selected, callback, symmetries):
      self.callback = callback
      self.symmetries = symmetries
      self.cell = selected
      self.northwall.current(self.doorways.index(selected.wall(Direction.North).name))
      self.eastwall.current(self.doorways.index(selected.wall(Direction.East).name))
      self.southwall.current(self.doorways.index(selected.wall(Direction.South).name))
      self.westwall.current(self.doorways.index(selected.wall(Direction.West).name))
      self.show()
      return


if __name__ == "__main__":
   root = Tk()
   # noinspection PyUnboundLocalVariable
   cell = Cell(1, 2)
   cell.setWalls("oxhb")
   app = KnotCellEdit(root)
   # noinspection PyUnboundLocalVariable
   app.set(cell, None, Symmetry.No)
   root.mainloop()
