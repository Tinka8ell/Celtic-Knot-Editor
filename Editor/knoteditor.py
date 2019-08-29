# Simple KnotEditor framework

import os#, sys, random

from tkinter import *
from tkinter import ttk
from tkinter import font
from tkinter import filedialog

from knot import Knot
from knotcelledit import KnotCellEdit
from cell import Cell
from utils import KnotConfirm, KnotInfo, KnotError
from enums import Symmetry, Direction


class KnotEditor(Frame):

   # values for radio bottons:
   rotateNone = 0
   rotate90 = 1
   rotate180 = 2

   pasteChange = 0
   pasteSet = 1
   pasteOverlay = 2
   pasteUnderlay = 3
   
   def __init__(self, master=None):
      super().__init__(master)
      self.master = master
      self.master.title("Knot Editor")
      self.knot = None
      self.cellEditor = None
      self.saved = True
      self.filename = None
      self.lastdir = None
      self.pos = None
      self.x = None
      self.y = None
      self.tox = None
      self.toy = None
      self.symmetries = Symmetry.No
      self.create_widgets()

   def create_widgets(self):
      # Create and grid the outer content frame
      master = self
      frame = self.master
      master.grid_columnconfigure(0, weight=1)
      master.grid_rowconfigure(0,weight=1)
      frame.grid_columnconfigure(0, weight=1)
      frame.grid_rowconfigure(0,weight=1)

      commonRow = 0
      commonCol = 0
      detailsRow = commonRow
      detailsCol = commonCol
      detailsWidth = 1
      displayRow = commonRow
      displayCol = commonCol + detailsWidth
      displayWidth = 1
      displayHeight = 1
      scrollRow = displayRow + displayHeight
      scrollCol = displayCol + displayWidth
      buttonRow = scrollRow + 1
      buttonCol = commonCol
      buttonWidth = displayWidth + detailsWidth

      # Knot display area:
      self.fontSize = 18
      self.font = font.Font(family="KNOTS Zoo", size=self.fontSize)
      self.text = Text(frame, height=5, width = 20, wrap="none", font=self.font)
      self.text.grid(column=displayCol, row=displayRow, columnspan=displayWidth, rowspan=displayHeight, sticky=(N,W,E,S))
      self.foreground = self.text["foreground"]
      self.background = self.text["background"]
      self.text.configure(state="disabled")
      self.dragging = False
      self.text.bind("<ButtonPress-1>", self.pressed)
      self.text.bind("<Motion>", self.motion)
      self.text.bind("<ButtonRelease-1>", self.released)
      # with linked scroll bars
      self.vs = ttk.Scrollbar(frame, orient=VERTICAL, command=self.text.yview)
      self.vs.grid(column=scrollCol, row=displayRow, rowspan=displayHeight, sticky=(N,S))
      self.hs = ttk.Scrollbar(frame, orient=HORIZONTAL, command=self.text.xview)
      self.hs.grid(column=displayCol, row=scrollRow, columnspan=displayWidth, sticky=(E,W))
      self.text['yscrollcommand'] = self.vs.set
      self.text['xscrollcommand'] = self.hs.set

      # details
      self.detailArea = Frame(frame) 
      self.detailArea.grid(column=detailsCol, row=detailsRow, rowspan=buttonWidth, sticky=(N,E,W,S))
      # size
      self.size = ttk.Labelframe(self.detailArea, text='Size:')
      self.size.grid(column=0, row=0, sticky=(N,E,W,S))
      self.size.wLabel = Label(self.size, text="Width:")
      self.size.wLabel.grid(column=1, row=0, sticky=(E))
      self.size.width = IntVar()
      self.size.width.set(20)
      self.size.wEntry = ttk.Entry(self.size, textvariable=self.size.width, width=3)
      self.size.wEntry.grid(column=2, row=0, sticky=(W))
      self.size.hLabel = Label(self.size, text="Height:")
      self.size.hLabel.grid(column=1, row=1, sticky=(E))
      self.size.height = IntVar()
      self.size.height.set(7)
      self.size.hEntry = ttk.Entry(self.size, textvariable=self.size.height, width=3)
      self.size.hEntry.grid(column=2, row=1, sticky=(W))
      self.size.fLabel = Label(self.size, text="Cell size:")
      self.size.fLabel.grid(column=1, row=2, sticky=(E))
      self.size.font = IntVar()
      self.size.font.set(self.fontSize)
      self.size.fEntry = ttk.Entry(self.size, textvariable=self.size.font, width=3)
      self.size.fEntry.grid(column=2, row=2, sticky=(W))
      self.size.fEntry.bind('<Key-Return>', self.fontSizeChanged)
      self.size.fEntry.bind('<FocusOut>', self.fontSizeChanged)
      # symmetry
      self.symmetry = ttk.Labelframe(self.detailArea, text='Symmetry:')
      self.symmetry.grid(column=1, row=0, sticky=(N,E,W,S))
      self.symmetry.vertMirror = BooleanVar()
      self.symmetry.vertMirror.set(False)
      self.symmetry.vmCheck = ttk.Checkbutton(self.symmetry, text='Vertical Mirror', variable=self.symmetry.vertMirror, command=self.vertMirrorChanged)
      self.symmetry.vmCheck.grid(column=0, row=2, columnspan=3, sticky=(W))
      self.symmetry.horizMirror = BooleanVar()
      self.symmetry.horizMirror.set(False)
      self.symmetry.hmCheck = ttk.Checkbutton(self.symmetry, text='Horizontal Mirror', variable=self.symmetry.horizMirror, command=self.horizMirrorChanged)
      self.symmetry.hmCheck.grid(column=0, row=3, columnspan=3, sticky=(W))
      self.symmetry.rLabel = Label(self.symmetry, text="Rotation:")
      self.symmetry.rLabel.grid(column=0, row=4, columnspan=3, sticky=(W))
      self.symmetry.rotation = IntVar()
      self.symmetry.rotation.set(0)
      self.symmetry.rNone = ttk.Radiobutton(self.symmetry, text='None', variable=self.symmetry.rotation, value=self.rotateNone, command=self.rotationChanged)
      self.symmetry.rNone.grid(column=0, row=5)
      self.symmetry.r180 = ttk.Radiobutton(self.symmetry, text='180', variable=self.symmetry.rotation, value=self.rotate180, command=self.rotationChanged)
      self.symmetry.r180.grid(column=1, row=5)
      self.symmetry.r90 = ttk.Radiobutton(self.symmetry, text='90', variable=self.symmetry.rotation, value=self.rotate90, command=self.rotationChanged)
      self.symmetry.r90.grid(column=2, row=5)
      # options
      self.options = ttk.Labelframe(self.detailArea, text='Options:')
      self.options.grid(column=0, row=1, columnspan=2, sticky=(N,E,W,S))
      self.options.visible = BooleanVar()
      self.options.visible.set(True)
      self.visibleChanged()
      self.options.vLabel = Label(self.options, text="Marked is visible:")
      self.options.vLabel.grid(column=0, row=0, columnspan=4, sticky=(W))
      self.options.vTrue = ttk.Radiobutton(self.options, text='Yes', variable=self.options.visible, value=True, command=self.visibleChanged)
      self.options.vTrue.grid(column=0, row=1, sticky=(W))
      self.options.vFalse = ttk.Radiobutton(self.options, text='No', variable=self.options.visible, value=False, command=self.visibleChanged)
      self.options.vFalse.grid(column=1, row=1, sticky=(W))
      self.options.pLabel = Label(self.options, text="Paste mode:")
      self.options.pLabel.grid(column=0, row=2, columnspan=4, sticky=(W))
      self.options.pasteMode = IntVar()
      self.pasteMode = self.pasteChange
      self.options.pasteMode.set(self.pasteMode)
      self.options.rChange = ttk.Radiobutton(self.options, text='Change', variable=self.options.pasteMode, value=self.pasteChange, command=self.pasteChanged)
      self.options.rChange.grid(column=0, row=3, sticky=(W))
      self.options.rSet = ttk.Radiobutton(self.options, text='Set', variable=self.options.pasteMode, value=self.pasteSet, command=self.pasteChanged)
      self.options.rSet.grid(column=1, row=3, sticky=(W))
      self.options.rOverlay = ttk.Radiobutton(self.options, text='Overlay', variable=self.options.pasteMode, value=self.pasteOverlay, command=self.pasteChanged)
      self.options.rOverlay.grid(column=2, row=3, sticky=(W))
      self.options.rUnderlay = ttk.Radiobutton(self.options, text='Underlay', variable=self.options.pasteMode, value=self.pasteUnderlay, command=self.pasteChanged)
      self.options.rUnderlay.grid(column=3, row=3, sticky=(W))
      # cell edit
      self.edit = ttk.Labelframe(self.detailArea, text='Cell editor')
      self.edit.grid(column=0, row=2, columnspan=2, sticky=(N,E,W,S))
      self.cellEditor = KnotCellEdit(self.edit)
      self.cellEditor.grid(column=0, row=0, sticky=(E))

      # buttons
      self.buttonStrip = Frame(frame) 
      self.buttonStrip.grid(column=buttonCol, row=buttonRow, columnspan=buttonWidth, sticky=(N,E,W,S))
      self.buttonNew = Button(self.buttonStrip, text="New", command=self.new)
      self.buttonQuit = Button(self.buttonStrip, text="Quit", command=self.quit)
      self.buttonLoad = Button(self.buttonStrip, text="Load", command=self.load)
      self.buttonSave = Button(self.buttonStrip, text="Save", command=self.save)
      self.buttonGen = Button(self.buttonStrip, text="Generate", command=self.generate)
      self.buttonCopy = Button(self.buttonStrip, text="Copy", command=self.copy)
      self.buttonPaste = Button(self.buttonStrip, text="Paste", command=self.paste)
      self.buttonNew.grid(column=0, row=0, pady=5, padx=5)
      self.buttonLoad.grid(column=1, row=0, pady=5, padx=5)
      self.buttonSave.grid(column=2, row=0, pady=5, padx=5)
      self.buttonGen.grid(column=3, row=0, pady=5, padx=5)
      self.buttonCopy.grid(column=4, row=0, pady=5, padx=5)
      self.buttonPaste.grid(column=5, row=0, pady=5, padx=5)
      self.buttonQuit.grid(column=6, row=0, pady=5, padx=5)

      # make it stretchy
      maxCol = max(displayCol, buttonCol, scrollCol, detailsCol)
      maxRow = max(displayRow, buttonRow, scrollRow, detailsRow)
      ttk.Sizegrip(frame).grid(column=maxCol, row=maxRow, sticky=(S,E))
      # but only the display
      for col in range(displayCol):
         frame.grid_columnconfigure(col, weight=0)
      for col in range(displayCol, displayCol + displayWidth):
         frame.grid_columnconfigure(col, weight=3)
      for col in range(displayCol + displayWidth, maxCol):
         frame.grid_columnconfigure(col, weight=0)
      for row in range(displayRow):
         frame.grid_rowconfigure(row, weight=0)
      for row in range(displayRow, displayRow + displayHeight):
         frame.grid_rowconfigure(row, weight=3)
      for row in range(displayRow + displayHeight, maxRow):
         frame.grid_rowconfigure(row, weight=0)
      return

   def visibleChanged(self):#, event):
      visible = self.options.visible.get()
      if visible:
         self.markFore = self.background
         self.markBack = self.foreground
      else:
         self.markFore = self.foreground
         self.markBack = self.background
      self.text.tag_configure("mark", background = self.markBack, foreground = self.markFore)
      # make normal select invisible!
      self.text.configure(selectbackground = self.background, selectforeground = self.foreground)
      return

   def fontSizeChanged(self, event):
      size = self.size.font.get()
      if size != self.fontSize:
         self.fontSize = size
         self.font = font.Font(family="KNOTS Zoo", size=self.fontSize)
         self.text.configure(font=self.font)
         self.show()
      return      

   def vertMirrorChanged(self):
      mirror = self.symmetry.vertMirror.get()
      self.symmetries &= ~Symmetry.Vertical # ensure off
      if mirror:
         self.symmetries |= Symmetry.Vertical # only set on if ticked
      if self.knot:
         self.cellEditor.update(self.symmetries) # so cell editor picks up changes
      return
   
   def horizMirrorChanged(self):
      mirror = self.symmetry.horizMirror.get()
      self.symmetries &= ~Symmetry.Horizontal # ensure off
      if mirror:
         self.symmetries |= Symmetry.Horizontal # only set on if ticked
      if self.knot:
         self.cellEditor.update(self.symmetries) # so cell editor picks up changes
      return
   
   def rotationChanged(self):
      rotation = self.symmetry.rotation.get()
      self.symmetries &= ~(Symmetry.Rotate90 | Symmetry.Rotate180 | Symmetry.Rotate270) # ensure all off
      if rotation == self.rotate90:
         self.symmetries |= Symmetry.Rotate90 # only set on if selected
      if rotation == self.rotate180:
         self.symmetries |= Symmetry.Rotate180 # only set on if selected
      # else leave unset if rotateNone
      if self.knot:
         self.cellEditor.update(self.symmetries) # so cell editor picks up changes
      return

   def pasteChanged(self):
      self.pasteMode = self.options.pasteMode.get()
      return

   def new(self):
      if not self.saved:
         response = KnotConfirm("Unsaved knot! \nDo you want to create a new one without saving it?")
         if response:
            self._new()
      else:
         self._new()
      return

   def _new(self):
      self.setKnot(Knot(self.getWidth(), self.getHeight()))
      self.resetCellEditor()
      return

   def resetCellEditor(self):
      self.pos = None
      self.x = None
      self.y = None
      if self.knot:
         self.cellEditor.reset() # so cell editor picks up changes
      return

   def quit(self):
      if not self.saved:
         response = KnotConfirm("Unsaved knot! \nDo you want to quit without saving it?")
         if response:
            self._quit()
      else:
         self._quit()
      return

   def _quit(self):
      self.master.destroy()
      return

   def load(self):
      if not self.saved:
         response = KnotConfirm("Unsaved knot! \nDo you want to load without saving it?")
         if response:
            self._load()
      else:
         self._load()
      return

   def _load(self):
      self.filename = filedialog.askopenfilename(initialdir = self.lastdir, title = "Load knot file", filetypes = (("text files","*.txt"),("all files","*.*")))
      if self.filename != "":
         self.lastdir = os.path.dirname(self.filename)
         with open(self.filename) as f:
            knot = f.read()
         if knot and knot != "":
            self.setKnot(Knot.load(knot))
            self.saved = True
            self.resetCellEditor()
         else:
            KnotInfo("Nothing read in!")
      return

   def save(self):
      if (self.knot):
         self.filename = filedialog.asksaveasfilename(initialdir = self.lastdir, title = "Save knot file", filetypes = (("text files","*.txt"),("all files","*.*")), defaultextension = ".txt")
         if self.filename != "":
            self.lastdir = os.path.dirname(self.filename)
            with open(self.filename, 'w') as f:
               f.write(self.knot.show())
            self.saved = True
      else:
         KnotError("You will need load or generate a knot first!")
      return

   def generate(self):
      if not self.saved:
         response = KnotConfirm("Unsaved knot! \nDo you want to generate a new one without saving the old one?")
         if response:
            self._generate()
      else:
         self._generate()
      return

   def _generate(self):
      print("Generate called")
      self.saved = False
      self.resetCellEditor()
      return

   def setText(self, text):
      self.text.configure(state="normal")
      self.text.delete("1.0", "end")
      self.text.insert("end", text)
      self.text.configure(state="disabled")
      return

   def setKnot(self, knot):
      self.knot = knot
      self.size.width.set(knot.width)
      self.size.height.set(knot.height)
      self.show()
      return

   def show(self):
      text = ""
      if self.knot:
         text = self.knot.print()
      self.setText(text)
      return

   def pressed(self, event):
      # place where button pressed
      if self.knot:
         self.x, self.y, self.pos = self.getPos(event) # remember where we are for later
         ### print("Pressed:", self.x, self.y, self.pos)
         self.dragging = True
         # so we can see where the selection starts from ...
         self.tox = self.x
         self.toy = self.y
         # check still in knot
         cell = None
         try:
            cell = self.knot.cell(self.x, self.y)
         except:
            # ignore out of range, just set no cell
            cell = None
         if cell:
            self.mark() # so we can see what we clicked?
         else:
            self.cellEditor.reset()
      else:
         KnotInfo("No knot yet!")
      return

   def motion(self, event):
      # place where mouse moved
      if self.dragging: # only care while dragging!
         self.tox, self.toy, self.pos = self.getPos(event) # we are now here
         ### print("Moved:", self.tox, self.toy, self.pos)
         # check still in knot
         cell = None
         try:
            cell = self.knot.cell(self.tox, self.toy)
         except:
            # ignore out of range, just set no cell
            cell = None
         if cell:
            self.mark() # so we can see what we clicked?
      return

   def getPos(self, event):
      # place where mouse is in event
      # convert pixel address (@x,y) to character index (r.c)
      pos = self.text.index("@%d,%d" % (event.x, event.y))
      # convert character index (r.c) to knot cell position (indexed from 0)
      dot = pos.index(".")
      x = int(pos[dot+1:])
      y = int(pos[0: dot]) - 1
      return (x, y, pos)

   def released(self, event):
      # place where button pressed
      if self.knot:
         # so we can see where the selection ends ...
         self.tox, self.toy, self.pos = self.getPos(event)
         ### print("Released:", self.tox, self.toy, self.pos)
         self.dragging = False
         # check still in knot
         cell = None
         try:
            cell = self.knot.cell(self.x, self.y) # original corner
         except:
            # ignore out of range, just set no cell
            cell = None
         if cell:
            self.mark() # so we can see what we sellected?
            self.cellEditor.set(cell, self.cellChanged, self.symmetries)
         else:
            self.cellEditor.reset()
      else:
         KnotInfo("No knot yet!")
      return

   def mark(self):
      col = self.x
      cols = self.tox - self.x + 1
      row = self.y + 1
      rows = self.toy - self.y + 1
      self.text.configure(state="normal")
      self.text.tag_delete("mark")
      for i in range(rows):
         pos = str(row + i) + "." + str(col)
         self.text.tag_add("mark", pos, pos + "+" + str(cols) + "c")
      self.text.tag_configure("mark", background = self.markBack, foreground = self.markFore)
      self.text.configure(state="disabled")
      return

   def copy(self):
      col = self.x
      cols = self.tox - self.x + 1
      row = self.y
      rows = self.toy - self.y + 1
      self.clip = []
      for y in range(rows):
         thisrow = []
         for x in range(cols):
            cell = Cell(x, y)
            source = self.knot.cell(x + col, y + row)
            # copy the walls to new clip cell
            for d in Direction:
               cell.setWall(d, source.wall(d))
            thisrow.append(cell)
         self.clip.append(thisrow)
      # now have a copy of cell walls in clip
      return

   def paste(self):
      col = self.x
      cols = len(self.clip[0]) # use 1st row as all rows are the same in clip
      row = self.y
      rows = len(self.clip) # number of rows in clip
      for y in range(rows):
         for x in range(cols):
            dest = None
            try:
               dest = self.knot.cell(x + col, y + row)
            except:
               # skip out of range, just set no cell
               dest = None
            if dest:
               cell = self.clip[y][x]
               # set the walls from the clip cell to the destination
               if self.pasteMode == self.pasteSet:
                  for d in Direction:
                     dest.setWall(d, cell.wall(d))
               if self.pasteMode == self.pasteChange:
                  for d in Direction:
                     dest.changeWall(d, cell.wall(d), self.symmetries)
               if self.pasteMode == self.pasteOverlay:
                  if not cell.empty(): # only blocked or remove on all walls
                     for d in Direction:
                        dest.setWall(d, cell.wall(d))
               if self.pasteMode == self.pasteUnderlay:
                  if dest.empty(): # only blocked or remove on all walls
                     for d in Direction:
                        dest.setWall(d, cell.wall(d))
      self.show()
      return

   def cellChanged(self):
      self.show()
      self.saved = False
      self.text.see(self.pos) # make sure what we changed is visible!
      return

   def getWidth(self):
      return self.size.width.get()

   def setWidth(self, number):
      self.size.width.set(number)
      return 

   def getHeight(self):
      return self.size.height.get()

   def setHeight(self, number):
      self.size.height.set(number)
      return 


if __name__ == "__main__":
   binary = (0b01000010, 0b01101001, 0b01100001, 0b01101110, 0b01110010, 0b01111001)
   text = ""
   for b in binary:
      text += chr(b)
   print(text)
   map = '''oooooooooxxoooxx
oxxooxixxxxxxoox
xixoIIIIxoxi
xxooixoxxxxxooxxoooooxxoooxxxxooixoxxxxxooxxoooooxxoooxx
ooooooooxxooxxxxoxixxxxxxooxooooooooxxooxxxxoxixxxxxxoox
ooooooooooooxixoIIIIxoxiooooooooooooooooxixoIIIIxoxioooo
oooooooooxxoooxx
oxxooxixxxxxxoox
xixoIIIIxoxi
xxooixoxxxxxooxxoooooxxoooxx
ooooooooxxooxxxxoxixxxxxxoox
ooooooooooooxixoIIIIxoxioooo'''
   ''' # this and map were for testing, ignored now
   knot = Knot.load(map)
   print("Knot show:")
   print(knot.show())
   print("Knot print:")
   print(knot.print())
   '''
   
   root = Tk()
   editor = KnotEditor(master=root)
   # editor.setKnot(knot)
   editor.mainloop()
