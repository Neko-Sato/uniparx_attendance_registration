from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Callable, Optional
import tkinter as tk

if TYPE_CHECKING:
  from .page import Page

PageBuilder = Callable[["Screen"], "Page"]

class Screen(tk.Frame):
  current_pages: Optional["Page"]
  def __init__(self, master) -> None:
    super().__init__(master)
    self.current_pages = None
  def display(self, builder:Optional["PageBuilder"]) -> None:
    if builder is not None:
      page = builder(self)
      page.pack()
    if self.current_pages is not None:
      self.current_pages.destroy()
    self.current_pages = page
  @classmethod
  def of(cls, widget:tk.Widget) -> Optional["Screen"]:
    master = getattr(widget, "master", None)
    if isinstance(master, cls) or master is None:
      return master
    else:
      return cls.of(master)