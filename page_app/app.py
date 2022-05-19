from typing import Optional
import tkinter as tk

from .screen import Screen

class App(tk.Tk):
  screen:"Screen"
  def __init__(self) -> None:
    super().__init__()
    self.screen = Screen(self)
    self.screen.pack()
  @classmethod
  def of(cls, widget:tk.Widget) -> Optional["App"]:
    master = getattr(widget, "master", None)
    if isinstance(master, cls) or master is None:
      return master
    else:
      return cls.of(master)
