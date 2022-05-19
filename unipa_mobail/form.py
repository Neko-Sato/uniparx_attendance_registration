from typing import List, Dict
from bs4 import BeautifulSoup
import re

from .exceptions import FormNotFound

class FormComponent:
  name:str
  value:str
  def __init__(self, name:str, value:str) -> None:
    self.name = name
    self.value = value
  def __repr__(self) -> str:
    return f"<{self.__class__.__name__} name={self.name} value={self.value}>"

class InputFormComponent(FormComponent):
  def __init__(self, soup:BeautifulSoup) -> None:
    super().__init__(soup.attrs.get("name"), soup.attrs.get("value"))

class SelectFormComponent(FormComponent):
  def __init__(self, soup:BeautifulSoup) -> None: 
    option = soup.find("option")
    super().__init__(soup.attrs.get("name"), option.attrs.get("value"))

class ButtonFormComponent(FormComponent):
  def __init__(self, soup:BeautifulSoup) -> None:
    super().__init__(soup.attrs.get("name"), "")

class AFormComponent(FormComponent):
  def __init__(self, soup:BeautifulSoup) -> None:
    super().__init__(soup.attrs.get("id"), soup.attrs.get("id"))

class Form:
  soup:BeautifulSoup
  path:str
  method:str
  args:List[FormComponent]
  args_required:List[FormComponent]
  funs:List[FormComponent]
  def __init__(self, soup:BeautifulSoup, name:str) -> None:
    self.soup = soup.find("form", attrs={"name": name})
    if self.soup is None:
      raise FormNotFound()

    self.path = self.soup.attrs.get("action")
    self.method = self.soup.attrs.get("method")
    self.content_type = self.soup.attrs.get("enctype")

    self.args = []
    self.args_required = []
    self.funs = []

    for i in self.soup.find_all("input"):
      if f"{name}:" not in i.attrs.get("name"):
        self.args_required.append(InputFormComponent(i))
      else:
        self.args.append(InputFormComponent(i))
    for i in self.soup.find_all("select"):
        self.args.append(SelectFormComponent(i))
    for i in self.soup.find_all("button"):
      self.funs.append(ButtonFormComponent(i))
    for i in self.soup.find_all("a", id=re.compile(f"^{name}:.*$")):
      self.funs.append(AFormComponent(i))
  def __getitem__(self, name) -> FormComponent:
    return self.find(name)
  def find(self, name, args:bool=True, funs:bool=True, args_required:bool=True):
    return next(self.__find_generator(name, args, funs, args_required), None)
  def find_all(self, name, args:bool=True, funs:bool=True, args_required:bool=True):
    return list(self.__find_generator(name, args, funs, args_required))
  def __find_generator(self, name, args:bool=True, funs:bool=True, args_required:bool=True):
    if not isinstance(name, re.Pattern):
      name = re.compile(f"^{name}$")
    target = [
      *(self.args if args else []), 
      *(self.funs if funs else []), 
      *(self.args_required if args_required else []),
    ]
    for i in target:
      if name.match(i.name):
        yield i
  def get_request_args(self, fun:FormComponent, *args:FormComponent) -> Dict:
    result = {
      "path": self.path,
      "method": self.method,
      "headers": {
        "content-type" : self.content_type,
      },
      "data": [(i.name, i.value) for i in [fun, *args, *self.args_required]],
    }
    return result
