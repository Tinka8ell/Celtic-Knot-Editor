# !/usr/bin/python3
# ShowMe.py
from tkinter import * 
from tkinter import ttk
from tkinter import font

from knot import Cell, Direction, Doorway, Ligature, Symmetry

class KnotCellEdit(Frame):
   def __init__(self, master=None):
      super().__init__(master)
      self.master = master
      self.cell = None
      self.callback = None
      self.symmetries = Symmetry.No
      self.create_widgets()

   def create_widgets(self):
      master = self
      frame = self.master
      self.frame = frame
      master.grid_columnconfigure(0, weight=1)
      master.grid_rowconfigure(0,weight=1)
      frame.grid_columnconfigure(0, weight=1)
      frame.grid_columnconfigure(1, weight=1)
      frame.grid_columnconfigure(2, weight=1)
      frame.grid_rowconfigure(0,weight=1)
      frame.grid_rowconfigure(1,weight=1)
      frame.grid_rowconfigure(2,weight=1)

      self.font = font.Font(family="KNOTS Zoo", size=72)
      self.view = Label(self.frame, text="O", font=self.font)
      self.view.grid(row=1, column=1, sticky=(N,W,E,S))

      self.doorways = list(Doorway.__members__.keys())
      chars = 0
      for door in self.doorways:
         chars = max(chars, len(door))
      self.northwall = ttk.Combobox(self.frame, values = list(self.doorways), width = chars)
      self.northwall.grid(row=0, column=1)
      self.northwall.bind("<<ComboboxSelected>>", self.changeNorthWall)
      self.eastwall = ttk.Combobox(self.frame, values = list(self.doorways), width = chars)
      self.eastwall.grid(row=1, column=2)
      self.eastwall.bind("<<ComboboxSelected>>", self.changeEastWall)
      self.southwall = ttk.Combobox(self.frame, values = list(self.doorways), width = chars)
      self.southwall.grid(row=2, column=1)
      self.southwall.bind("<<ComboboxSelected>>", self.changeSouthWall)
      self.westwall = ttk.Combobox(self.frame, values = list(self.doorways), width = chars)
      self.westwall.grid(row=1, column=0)
      self.westwall.bind("<<ComboboxSelected>>", self.changeWestWall)
      self.reset()
      return

   def reset(self):
      self.cell = None
      self.view["text"] = "O"
      self.northwall.current(0)
      self.eastwall.current(0)
      self.southwall.current(0)
      self.westwall.current(0)
      return

   def changeNorthWall(self, event):
      self.changeWall(event, Doorway[self.northwall.get()], Direction.North)
      return
        
   def changeEastWall(self, event):
      self.changeWall(event, Doorway[self.eastwall.get()], Direction.East)
      return
        
   def changeSouthWall(self, event):
      self.changeWall(event, Doorway[self.southwall.get()], Direction.South)
      return
        
   def changeWestWall(self, event):
      self.changeWall(event, Doorway[self.westwall.get()], Direction.West)
      return
        
   def changeWall(self, event, doorway, direction):
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

   def update(self, symmetries):
      self.symmetries = symmetries
      return

   def set(self, cell, callback, symmetries):
      self.callback = callback
      self.symmetries = symmetries
      self.cell = cell
      self.northwall.current(self.doorways.index(cell.wall(Direction.North).name))
      self.eastwall.current(self.doorways.index(cell.wall(Direction.East).name))
      self.southwall.current(self.doorways.index(cell.wall(Direction.South).name))
      self.westwall.current(self.doorways.index(cell.wall(Direction.West).name))
      self.show()
      return

if __name__ == "__main__":
   root = Tk()
   cell = Cell(1, 2)
   cell.setWalls("oxhb")
   app = KnotCellEdit(root)
   app.set(cell, None, Symmetry.No)
   root.mainloop()
