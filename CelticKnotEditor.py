"""
Celtic Knot Editor

An editor using KnotZoo font to create and manipulate Celtic Knot patterns.
This project was created as an aid to creating simple Celtic knots and trying out ideas.
It is using the KnotZoo font developed by Ben Griffin (https://github.com/MrBenGriffin).
I hope to link to his knot generator [Knotwork](https://github.com/MrBenGriffin/Knot) 
as a way of seeding a knot.
I further hope to develop the font to support "removed" ligature 
to generate single line borders.
"""

from tkinter import Tk

from Editor.knoteditor import KnotEditor


if __name__ == "__main__":
    root = Tk()
    editor = KnotEditor(master=root)
    editor.mainloop()
