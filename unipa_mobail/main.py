from __future__ import annotations
from calendar import c
from typing import TYPE_CHECKING, Optional
import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

from .form import Form
from .exceptions import *

if TYPE_CHECKING:
  from .actions import Action

class UnipaMobail:
  HOST:str = "https://unipa.i-u.ac.jp"
  session:requests.Session
  current_soup:Optional[BeautifulSoup]
  current_action:"Action"
  user_id:str
  user_paswrd:str
  def __init__(self, user_id:str, user_paswrd:str):
    self.session =  requests.Session()
    self.current_soup = None
    self.current_action = None
    self.user_id = user_id
    self.user_paswrd =  user_paswrd
    self.login()
  def login(self):
    self.update_soup(method="post", path='/uprx/up/pk/pky501/Pky50101.xhtml', certification=False)
    loginForm = self.get_form("pmPage:loginForm")
    loginForm.args[0].value = self.user_id
    loginForm.args[1].value = self.user_paswrd
    values = loginForm.get_request_args(
      loginForm.funs[0],
      loginForm.args[0],
      loginForm.args[1],
    )
    self.update_soup(**values, certification=False)
    if self.get_form("pmPage:loginForm") is not None:
      raise LoginError()
  def update_soup(self, path, data=[], certification=True, **kwargs):
    response = self.session.request(
      **kwargs, 
      url = self.HOST + path,
      data = urlencode(data),
      )
    if response.status_code == 503:
      raise MaintenanceError
    self.current_soup = BeautifulSoup(response.content, "html.parser")
    if certification and self.current_soup.find("form", id="pmPage:funcForm") is None:
      self.cancel_action()
      self.login()
      raise TimeoutError()
  def do_action(self, action:Action, *args, **kwargs):
    with action as opened_action:
      result = opened_action.execution(*args, kwargs)
    return result
  def cancel_action(self):
    if self.current_action is not None:
      self.current_action.close()
  def get_form(self, name):
    try:
      return Form(self.current_soup, name)
    except FormNotFound:
      return None

