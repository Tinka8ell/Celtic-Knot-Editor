from tkinter import Tk

from Editor.knoteditor import KnotEditor

if __name__ == "__main__":
    root = Tk()
    editor = KnotEditor(master=root)
    editor.mainloop()
