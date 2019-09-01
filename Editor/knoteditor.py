# Simple KnotEditor framework

import random

try:
   # noinspection PyUnresolvedReferences
   from Maze.maze import Maze
   # As we loaded it we can use it
   # Assumes a text.py and related packages are in the path
   ### print("we imported text")
   CanGenerate = True
   # noinspection PyUnresolvedReferences
   from Bod.mazer import Mazer
   # noinspection PyUnresolvedReferences
   from Bod.clone import Clone
   # noinspection PyUnresolvedReferences
   from Maze.util import Tweak
   # noinspection PyUnresolvedReferences
   from Maze.wall import Wall

except ImportError as e:
   # Otherwise we can;t use it
   ### print("we got ImportError:", e)
   CanGenerate = False   # noinspection PyUnresolvedReferences


import os

from tkinter import *
from tkinter import filedialog
from tkinter import font
from tkinter import ttk

try:
   # noinspection PyUnresolvedReferences
   from enums import Symmetry, Direction
   ### print("Got local version")
   local = True
except ModuleNotFoundError as e:
   ### print("Got package version")
   local = False
### print("setting for local is:", local)
if local:
   # noinspection PyUnresolvedReferences
   from cell import Cell
   # noinspection PyUnresolvedReferences
   from knotcelledit import KnotCellEdit
   # noinspection PyUnresolvedReferences
   from utils import KnotConfirm, KnotInfo, KnotError
   # noinspection PyUnresolvedReferences
   from knot import Knot
else:
   from Editor.cell import Cell
   from Editor.enums import Symmetry, Direction, Doorway
   from Editor.knotcelledit import KnotCellEdit
   from Editor.utils import KnotConfirm, KnotInfo, KnotError
   from Editor.knot import Knot


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
      master.option_add('*tearOff', FALSE)
      self.master.title("Knot Editor")
      self.knot = None
      self.cellEditor = None
      self.saved = True
      self.filename = None
      # noinspection SpellCheckingInspection
      self.lastdir = None
      self.pos = None
      self.x = None
      self.y = None
      self.tox = None
      self.toy = None
      self.symmetries = Symmetry.No
      self.foreground = None
      self.background = None
      self.markFore = None
      self.markBack = None
      self.fontSize = 18
      self.font = font.Font(family="KNOTS Zoo", size=self.fontSize)
      self.pasteMode = self.pasteChange
      self.dragging = False
      self.clip = []
      self.create_widgets()

   # noinspection PyAttributeOutsideInit,SpellCheckingInspection
   def create_widgets(self):
      # Create and grid the outer content frame
      master = self
      frame = self.master
      master.grid_columnconfigure(0, weight=1)
      master.grid_rowconfigure(0, weight=1)
      frame.grid_columnconfigure(0, weight=1)
      frame.grid_rowconfigure(0, weight=1)

      # Add menu items
      menubar = Menu(frame)
      frame['menu'] = menubar
      menu_file = Menu(menubar)
      menu_edit = Menu(menubar)
      menubar.add_cascade(menu=menu_file, label='File', underline=0)
      menubar.add_cascade(menu=menu_edit, label='Edit', underline=0)
      menu_file.add_command(label='New', command=self.new, underline=0, accelerator="ctrl+N")
      menu_file.add_command(label='Load...', command=self.load, underline=0, accelerator="ctrl+L")
      menu_file.add_command(label='Save...', command=self.save, underline=0, accelerator="ctrl+S")
      if CanGenerate:
         menu_file.add_command(label='Generate', command=self.generate, underline=0, accelerator="ctrl+G")
      menu_edit.add_command(label='Rotate', command=self.rotate, underline=0, accelerator="ctrl+R")
      menu_file.add_separator()
      menu_file.add_command(label='Exit', command=self.exit, underline=1, accelerator="ctrl+X")
      menu_edit.add_command(label='Copy', command=self.copy, underline=0, accelerator="ctrl+C")
      menu_edit.add_command(label='Delete', command=self.delete, underline=0, accelerator="ctrl+D")
      menu_edit.add_command(label='Paste', command=self.paste, underline=0, accelerator="ctrl+V")
      # Add keyboard short cuts
      frame.bind("<Control-n>", lambda event: self.new())
      frame.bind("<Control-l>", lambda event: self.load())
      frame.bind("<Control-s>", lambda event: self.save())
      if CanGenerate:
         frame.bind("<Control-g>", lambda event: self.generate())
      frame.bind("<Control-r>", lambda event: self.rotate())
      frame.bind("<Control-x>", lambda event: self.exit())
      frame.bind("<Control-c>", lambda event: self.copy())
      frame.bind("<Control-d>", lambda event: self.delete())
      frame.bind("<Control-v>", lambda event: self.paste())

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
      self.text = Text(frame, height=5, width=20, wrap="none", font=self.font)
      self.text.grid(column=displayCol, row=displayRow,
                     columnspan=displayWidth, rowspan=displayHeight, sticky=(N, W, E, S))
      self.foreground = self.text["foreground"]
      self.background = self.text["background"]
      self.text.configure(state="disabled")
      self.dragging = False
      self.text.bind("<ButtonPress-1>", self.pressed)
      self.text.bind("<Motion>", self.motion)
      self.text.bind("<ButtonRelease-1>", self.released)
      # with linked scroll bars
      self.vs = ttk.Scrollbar(frame, orient=VERTICAL, command=self.text.yview)
      self.vs.grid(column=scrollCol, row=displayRow, rowspan=displayHeight, sticky=(N, S))
      self.hs = ttk.Scrollbar(frame, orient=HORIZONTAL, command=self.text.xview)
      self.hs.grid(column=displayCol, row=scrollRow, columnspan=displayWidth, sticky=(E, W))
      self.text['yscrollcommand'] = self.vs.set
      self.text['xscrollcommand'] = self.hs.set

      # details
      self.detailArea = Frame(frame) 
      self.detailArea.grid(column=detailsCol, row=detailsRow, rowspan=buttonWidth, sticky=(N, E, W, S))
      # size
      self.size = ttk.Labelframe(self.detailArea, text='Size:')
      self.size.grid(column=0, row=0, sticky=(N, E, W, S))
      self.size_wLabel = Label(self.size, text="Width:")
      self.size_wLabel.grid(column=1, row=0, sticky=E)
      self.size_width = IntVar()
      self.size_width.set(20)
      self.size_wEntry = ttk.Entry(self.size, textvariable=self.size_width, width=3)
      self.size_wEntry.grid(column=2, row=0, sticky=W)
      self.size_hLabel = Label(self.size, text="Height:")
      self.size_hLabel.grid(column=1, row=1, sticky=E)
      self.size_height = IntVar()
      self.size_height.set(7)
      self.size_hEntry = ttk.Entry(self.size, textvariable=self.size_height, width=3)
      self.size_hEntry.grid(column=2, row=1, sticky=W)
      self.size_fLabel = Label(self.size, text="Cell size:")
      self.size_fLabel.grid(column=1, row=2, sticky=E)
      self.size_font = IntVar()
      self.size_font.set(self.fontSize)
      self.size_fEntry = ttk.Entry(self.size, textvariable=self.size_font, width=3)
      self.size_fEntry.grid(column=2, row=2, sticky=W)
      self.size_fEntry.bind('<Key-Return>', lambda event: self.fontSizeChanged())
      self.size_fEntry.bind('<FocusOut>', lambda event: self.fontSizeChanged())
      # symmetry
      self.symmetry = ttk.Labelframe(self.detailArea, text='Symmetry:')
      self.symmetry.grid(column=1, row=0, sticky=(N, E, W, S))
      self.symmetry_vertMirror = BooleanVar()
      self.symmetry_vertMirror.set(False)
      self.symmetry_vmCheck = ttk.Checkbutton(self.symmetry, text='Vertical Mirror',
                                              variable=self.symmetry_vertMirror, command=self.vertMirrorChanged)
      self.symmetry_vmCheck.grid(column=0, row=2, columnspan=3, sticky=W)
      self.symmetry_horizMirror = BooleanVar()
      self.symmetry_horizMirror.set(False)
      self.symmetry_hmCheck = ttk.Checkbutton(self.symmetry, text='Horizontal Mirror',
                                              variable=self.symmetry_horizMirror, command=self.horizMirrorChanged)
      self.symmetry_hmCheck.grid(column=0, row=3, columnspan=3, sticky=W)
      self.symmetry_rLabel = Label(self.symmetry, text="Rotation:")
      self.symmetry_rLabel.grid(column=0, row=4, columnspan=3, sticky=W)
      self.symmetry_rotation = IntVar()
      self.symmetry_rotation.set(0)
      self.symmetry_rNone = ttk.Radiobutton(self.symmetry, text='None', variable=self.symmetry_rotation,
                                            value=self.rotateNone, command=self.rotationChanged)
      self.symmetry_rNone.grid(column=0, row=5)
      self.symmetry_r180 = ttk.Radiobutton(self.symmetry, text='180', variable=self.symmetry_rotation,
                                           value=self.rotate180, command=self.rotationChanged)
      self.symmetry_r180.grid(column=1, row=5)
      self.symmetry_r90 = ttk.Radiobutton(self.symmetry, text='90', variable=self.symmetry_rotation,
                                          value=self.rotate90, command=self.rotationChanged)
      self.symmetry_r90.grid(column=2, row=5)
      # options
      self.options = ttk.Labelframe(self.detailArea, text='Options:')
      self.options.grid(column=0, row=1, columnspan=2, sticky=(N, E, W, S))
      self.options_visible = BooleanVar()
      self.options_visible.set(True)
      self.visibleChanged()
      self.options_vLabel = Label(self.options, text="Marked is visible:")
      self.options_vLabel.grid(column=0, row=0, columnspan=4, sticky=W)
      self.options_vTrue = ttk.Radiobutton(self.options, text='Yes', variable=self.options_visible,
                                           value=True, command=self.visibleChanged)
      self.options_vTrue.grid(column=0, row=1, sticky=W)
      self.options_vFalse = ttk.Radiobutton(self.options, text='No', variable=self.options_visible,
                                            value=False, command=self.visibleChanged)
      self.options_vFalse.grid(column=1, row=1, sticky=W)
      self.options_pLabel = Label(self.options, text="Paste mode:")
      self.options_pLabel.grid(column=0, row=2, columnspan=4, sticky=W)
      self.options_pasteMode = IntVar()
      self.options_pasteMode.set(self.pasteMode)
      self.options_rChange = ttk.Radiobutton(self.options, text='Change', variable=self.options_pasteMode,
                                             value=self.pasteChange, command=self.pasteChanged)
      self.options_rChange.grid(column=0, row=3, sticky=W)
      self.options_rSet = ttk.Radiobutton(self.options, text='Set', variable=self.options_pasteMode,
                                          value=self.pasteSet, command=self.pasteChanged)
      self.options_rSet.grid(column=1, row=3, sticky=W)
      self.options_rOverlay = ttk.Radiobutton(self.options, text='Overlay', variable=self.options_pasteMode,
                                              value=self.pasteOverlay, command=self.pasteChanged)
      self.options_rOverlay.grid(column=2, row=3, sticky=W)
      self.options_rUnderlay = ttk.Radiobutton(self.options, text='Underlay', variable=self.options_pasteMode,
                                               value=self.pasteUnderlay, command=self.pasteChanged)
      self.options_rUnderlay.grid(column=3, row=3, sticky=W)
      # cell edit
      self.edit = ttk.Labelframe(self.detailArea, text='Cell editor')
      self.edit.grid(column=0, row=2, columnspan=2, sticky=(N, E, W, S))
      self.cellEditor = KnotCellEdit(self.edit)
      self.cellEditor.grid(column=0, row=0, sticky=E)

      # buttons
      self.buttonStrip = Frame(frame) 
      self.buttonStrip.grid(column=buttonCol, row=buttonRow, columnspan=buttonWidth, sticky=(N, E, W, S))
      self.buttonNew = Button(self.buttonStrip, text="New", underline=0, command=self.new)
      self.buttonLoad = Button(self.buttonStrip, text="Load", underline=0, command=self.load)
      self.buttonSave = Button(self.buttonStrip, text="Save", underline=0, command=self.save)
      self.buttonRotate = Button(self.buttonStrip, text="Rotate", underline=0, command=self.rotate)
      if CanGenerate:
         self.buttonGen = Button(self.buttonStrip, text="Generate", underline=0, command=self.generate)
      self.buttonCopy = Button(self.buttonStrip, text="Copy", underline=0, command=self.copy)
      self.buttonDelete = Button(self.buttonStrip, text="Delete", underline=0, command=self.delete)
      self.buttonPaste = Button(self.buttonStrip, text="Paste", underline=0, command=self.paste)
      self.buttonQuit = Button(self.buttonStrip, text="Exit", underline=1, command=self.exit)
      self.buttonNew.grid(column=0, row=0, pady=5, padx=5)
      self.buttonLoad.grid(column=1, row=0, pady=5, padx=5)
      self.buttonSave.grid(column=2, row=0, pady=5, padx=5)
      if CanGenerate:
         self.buttonGen.grid(column=3, row=0, pady=5, padx=5)
      self.buttonRotate.grid(column=4, row=0, pady=5, padx=5)
      self.buttonCopy.grid(column=5, row=0, pady=5, padx=5)
      self.buttonDelete.grid(column=6, row=0, pady=5, padx=5)
      self.buttonPaste.grid(column=7, row=0, pady=5, padx=5)
      self.buttonQuit.grid(column=8, row=0, pady=5, padx=5)

      # make it stretchy
      maxCol = max(displayCol, buttonCol, scrollCol, detailsCol)
      maxRow = max(displayRow, buttonRow, scrollRow, detailsRow)
      ttk.Sizegrip(frame).grid(column=maxCol, row=maxRow, sticky=(S, E))
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

   def visibleChanged(self):
      visible = self.options_visible.get()
      if visible:
         self.markFore = self.background
         self.markBack = self.foreground
      else:
         self.markFore = self.foreground
         self.markBack = self.background
      self.text.tag_configure("mark", background=self.markBack, foreground=self.markFore)
      # make normal select invisible!
      self.text.configure(selectbackground=self.background, selectforeground=self.foreground)
      return

   def fontSizeChanged(self):
      size = self.size_font.get()
      if size != self.fontSize:
         self.fontSize = size
         self.font = font.Font(family="KNOTS Zoo", size=self.fontSize)
         self.text.configure(font=self.font)
         self.show()
      return      

   def vertMirrorChanged(self):
      mirror = self.symmetry_vertMirror.get()
      self.symmetries &= ~Symmetry.Vertical  # ensure off
      if mirror:
         self.symmetries |= Symmetry.Vertical  # only set on if ticked
      if self.knot:
         self.cellEditor.change(self.symmetries)  # so cell editor picks up changes
      return
   
   def horizMirrorChanged(self):
      mirror = self.symmetry_horizMirror.get()
      self.symmetries &= ~Symmetry.Horizontal  # ensure off
      if mirror:
         self.symmetries |= Symmetry.Horizontal  # only set on if ticked
      if self.knot:
         self.cellEditor.change(self.symmetries)  # so cell editor picks up changes
      return
   
   def rotationChanged(self):
      rotation = self.symmetry_rotation.get()
      self.symmetries &= ~(Symmetry.Rotate90 | Symmetry.Rotate180 | Symmetry.Rotate270)  # ensure all off
      if rotation == self.rotate90:
         self.symmetries |= Symmetry.Rotate90  # only set on if selected
      if rotation == self.rotate180:
         self.symmetries |= Symmetry.Rotate180  # only set on if selected
      # else leave unset if rotateNone
      if self.knot:
         self.cellEditor.change(self.symmetries)  # so cell editor picks up changes
      return

   def pasteChanged(self):
      self.pasteMode = self.options_pasteMode.get()
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
         self.cellEditor.reset()  # so cell editor picks up changes
      return

   def exit(self):
      if not self.saved:
         response = KnotConfirm("Unsaved knot! \nDo you want to quit without saving it?")
         if response:
            self.quit()
      else:
         self.quit()
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
      self.filename = filedialog.askopenfilename(initialdir=self.lastdir, title="Load knot file",
                                                 filetypes=(("text files", "*.txt"), ("all files", "*.*")))
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
      if self.knot:
         self.filename = filedialog.asksaveasfilename(initialdir=self.lastdir, title="Save knot file",
                                                      filetypes=(("text files", "*.txt"), ("all files", "*.*")),
                                                      defaultextension=".txt")
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
      random.seed(os.urandom(6))
      # collect dimentions and balances
      knot_work = Maze(self.getWidth(), self.getHeight(), 1, 0)
      Wall.straights_balance = self.straightsBalance
      Wall.zoomorph_balance = self.zoomorphBalance
      # create workers
      miner1 = Mazer(knot_work)
      miner1.dig(knot_work.entrance(Tweak(Tweak.master)))
      knot_work.add_bod(miner1, True)
      # add symmetries
      style = Tweak.master
      if self.symmetries & Symmetry.Rotate90:
         # must check we are square
         if self.getWidth() == self.getHeight():
            style = Tweak.rot090
         else:
            style = Tweak.rot180
      elif self.symmetries & Symmetry.Rotate180:
         style = Tweak.rot180
      elif self.symmetries & Symmetry.Vertical:
         style = Tweak.vanity
      elif self.symmetries & Symmetry.Horizontal:
         style = Tweak.horizon
      if style != Tweak.master:
         miner2 = Clone(knot_work, Tweak(style), miner1)
         miner2.dig(knot_work.entrance(miner2.tweak))
         knot_work.add_bod(miner2, True)
      if style == Tweak.rot090:
         miner3 = Clone(knot_work, Tweak(Tweak.rot180), miner1)
         miner4 = Clone(knot_work, Tweak(Tweak.rot270), miner1)
         miner3.dig(knot_work.entrance(miner3.tweak))
         miner4.dig(knot_work.entrance(miner4.tweak))
         knot_work.add_bod(miner3, True)
         knot_work.add_bod(miner4, True)
      knot_work.mine()
      self.setKnot(Knot.load(knot_work.code()))
      self.saved = False
      self.resetCellEditor()
      return

   def rotate(self):
      if self.knot:
         width = self.knot.width
         height = self.knot.height
         rotated = Knot(height, width)  # swap dimentions
         for y in range(height):
            for x in range(width):
               fromCell = self.knot.cell(x, y)
               toCell = rotated.cell(height - y - 1, x)
               for d in Direction:
                  toCell.setWall(d.cw, fromCell.wall(d))
         self.setKnot(rotated)
         self.saved = False
         self.resetCellEditor()
      else:
         KnotError("You will need load or generate a knot first!")
      return

   def setText(self, text):
      self.text.configure(state="normal")
      self.text.delete("1.0", "end")
      self.text.insert("end", text)
      self.text.configure(state="disabled")
      return

   def setKnot(self, knot):
      self.knot = knot
      self.size_width.set(knot.width)
      self.size_height.set(knot.height)
      self.show()
      return

   def show(self):
      text = ""
      if self.knot:
         text = self.knot.print()
      self.setText(text)
      return

   # noinspection PyUnusedLocal
   def pressed(self, event):
      # place where button pressed
      if self.knot:
         self.x, self.y, self.pos = self.getPos(event)  # remember where we are for later
         ### print("Pressed:", self.x, self.y, self.pos)
         self.dragging = True
         # so we can see where the selection starts from ...
         self.tox = self.x
         self.toy = self.y
         # check still in knot
         cell = None
         # noinspection PyBroadException
         try:
            cell = self.knot.cell(self.x, self.y)
         except:
            # ignore out of range, just set no cell
            cell = None
         if cell:
            self.mark()  # so we can see what we clicked?
         else:
            self.cellEditor.reset()
      else:
         KnotInfo("No knot yet!")
      return

   # noinspection PyUnusedLocal,PyBroadException
   def motion(self, event):
      # place where mouse moved
      if self.dragging:  # only care while dragging!
         self.tox, self.toy, self.pos = self.getPos(event)  # we are now here
         ### print("Moved:", self.tox, self.toy, self.pos)
         # check still in knot
         cell = None
         try:
            cell = self.knot.cell(self.tox, self.toy)
         except:
            # ignore out of range, just set no cell
            cell = None
         if cell:
            self.mark()  # so we can see what we clicked?
      return

   def getPos(self, event):
      # place where mouse is in event
      # convert pixel address (@x,y) to character index (r.c)
      pos = self.text.index("@%d,%d" % (event.x, event.y))
      # convert character index (r.c) to knot cell position (indexed from 0)
      dot = pos.index(".")
      x = int(pos[dot+1:])
      y = int(pos[0: dot]) - 1
      return x, y, pos

   # noinspection PyBroadException,PyUnusedLocal
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
            cell = self.knot.cell(self.x, self.y)  # original corner
         except:
            # ignore out of range, just set no cell
            cell = None
         if cell:
            self.mark()  # so we can see what we sellected?
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
      self.text.tag_configure("mark", background=self.markBack, foreground=self.markFore)
      self.text.configure(state="disabled")
      return

   def copy(self):
      col = self.x
      cols = self.tox - self.x + 1
      row = self.y
      rows = self.toy - self.y + 1
      self.clip = []
      for y in range(rows):
         thisRow = []
         for x in range(cols):
            cell = Cell(x, y)
            source = self.knot.cell(x + col, y + row)
            # copy the walls to new clip cell
            for d in Direction:
               cell.setWall(d, source.wall(d))
            thisRow.append(cell)
         self.clip.append(thisRow)
      # now have a copy of cell walls in clip
      return

   def delete(self):
      col = self.x
      cols = self.tox - self.x + 1
      row = self.y
      rows = self.toy - self.y + 1
      for y in range(rows):
         for x in range(cols):
            cell = self.knot.cell(x + col, y + row)
            # set or change all walls to blocked
            if self.pasteMode == self.pasteChange:
               for d in Direction:
                  cell.changeWall(d, Doorway.blocked, self.symmetries)
            else:  # all other modes are basically set ...
               for d in Direction:
                  cell.setWall(d, Doorway.blocked)
      self.saved = False
      self.show()
      return

   # noinspection PyUnusedLocal,PyBroadException
   def paste(self):
      col = self.x
      cols = len(self.clip[0])  # use 1st row as all rows are the same in clip
      row = self.y
      rows = len(self.clip)  # number of rows in clip
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
                  if not cell.isEmpty():  # only blocked or remove on all walls
                     for d in Direction:
                        dest.setWall(d, cell.wall(d))
               if self.pasteMode == self.pasteUnderlay:
                  if dest.isEmpty():  # only blocked or remove on all walls
                     for d in Direction:
                        dest.setWall(d, cell.wall(d))
      self.saved = False
      self.show()
      return

   def cellChanged(self):
      self.show()
      self.saved = False
      self.text.see(self.pos)  # make sure what we changed is visible!
      return

   def getWidth(self):
      return self.size_width.get()

   def setWidth(self, number):
      self.size_width.set(number)
      return 

   def getHeight(self):
      return self.size_height.get()

   def setHeight(self, number):
      self.size_height.set(number)
      return 


if __name__ == "__main__":
   # run the editor ...
   root = Tk()
   editor = KnotEditor(master=root)
   editor.mainloop()

   # Seen on a t-shirt:
   # "What part of: 0b01000010, 0b01101001, 0b01100001, 0b01101110, 0b01110010, 0b01111001 don't you understand?"
   # Couldn't do the binary to ascii in my head, so ... turns out to say "binary"!
   '''
   binary = (0b01000010, 0b01101001, 0b01100001, 0b01101110, 0b01110010, 0b01111001)
   text = ""
   for b in binary:
      text += chr(b)
   print(text)
   '''