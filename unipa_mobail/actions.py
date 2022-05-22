from __future__ import annotations
from typing import TYPE_CHECKING

from .exceptions import ActionError

if TYPE_CHECKING:
  from .main import UnipaMobail

class Action:
  unipa:UnipaMobail
  def __init__(self, unipa):
    self.isexecut = False
    self.unipa = unipa
  def __enter__(self):
    self.open()
    return self
  def __exit__(self, *exc):
    pass
  def deco_only_execution(fun):
    def warrper(self, *args, **kwargs):
      if not self.isexecut:
        raise ActionError()
      return fun(self, *args, **kwargs)
    return warrper
  def open(self):
    if self.unipa.current_action is not None:
      raise ActionError()
    self.isexecut = True
    try:
      self.initialization()
    except:
      self.close()
      raise
  @deco_only_execution
  def close(self):
    self.unipa.current_action = None
    self.isexecut = False
  @deco_only_execution
  def click_menu(self, name):
    menuForm = self.unipa.get_form("pmPage:menuForm")
    onclick = menuForm.soup.find("a", text=name).attrs["onclick"]
    button_name = menuForm.soup.find("button", class_=onclick[21:onclick.find("')")]).attrs["name"]
    values = menuForm.get_request_args(
      menuForm[button_name],
    )
    self.unipa.update_soup(**values)
  @deco_only_execution
  def initialization(self):
    pass
  @deco_only_execution
  def execution(self):
    self.close()