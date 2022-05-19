from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Optional
import tkinter as tk

if TYPE_CHECKING:
  from .screen import Screen

class Page(tk.Frame):
  def __init__(self, screen:"Screen") -> None:
    super().__init__(screen)
  @property
  def screen(self) -> Optional["Screen"]:
    return Screen.of(self)

class LabelPage(Page):
  def __init__(self, screen: "Screen", text:str="") -> None:
    super().__init__(screen)
    tk.Label(self, text=text).pack()