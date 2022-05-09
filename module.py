import requests
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup, Tag

class UnipaMobail:
  HOST = "https://unipa.i-u.ac.jp"
  def __init__(self, id, paswrd):
    self.session = requests.session()
    self.user_id = None
    self.nowsoup = None
    self.update_soup(path='/uprx/up/pk/pky501/Pky50101.xhtml')
    self.__login(id, paswrd)
  def __repr__(self):
    return f"<UnipaMobail {self.user_id}>"
  def update_soup(self, path, data=None, **kwargs):
    response = self.session.post(
      url = self.HOST + path,
      data = urlencode(data) if data is not None else None,
      **kwargs, 
      )
    self.nowsoup = BeautifulSoup(response.content, "html.parser")
  def get_form(self, name:str):
    return self.nowsoup.find('form', attrs={"name": name})
  def formatting(self, form:Tag):
    values = form.find_all(["input", "button"])
    result = {
      "path": form.attrs.get("action"),
      "headers": {
        "content-type" : form.attrs.get("enctype")
      },
      "data": {
        i.attrs.get("name"): i.attrs.get("value") if i.attrs.get("value") != None else "" 
        for i in values
      }
    }
    return result
  def __login(self, id, paswrd):
    if self.user_id is not None:
      print(self, "ログイン済み")
      return
    form = self.get_form("pmPage:loginForm")
    values = self.formatting(form)
    values["data"]["pmPage:loginForm:userId_input"] = id
    values["data"]["pmPage:loginForm:password"] = paswrd
    self.update_soup(**values)
    values = self.get_form("pmPage:menuForm")
    if values is None:
      print(self, "ログイン失敗")
    else:
      self.user_id = id
      print(self, "ログイン成功")
  def attend(self, code):
    if not re.match(r'^\d{4}$', code):
      print(self, "出席コードエラー")
      return
    form = self.get_form("pmPage:menuForm")
    values = self.formatting(form)
    values["data"] = {k:v for k, v in values["data"].items() if "pmPage:menuForm:" not in k}
    values["data"]["pmPage:menuForm:j_idt37:16:menuBtn1"] = ""
    self.update_soup(**values)
    form = self.get_form("pmPage:funcForm")
    if form.find(None, text="出席"):
      print(self, "出席済み")
      return
    values = self.formatting(form)
    del values["data"]["pmPage:funcForm:j_idt139"]
    values["data"] = { 
      k : v for k, v in values["data"].items()
      if not re.match(r'^pmPage:funcForm:j_idt90:\d+:j_idt(95|94|93)$', k)
    }
    code_input_form_name = [
      i for i in values["data"].keys() 
      if re.match(r'^pmPage:funcForm:j_idt90:\d+:j_idt\d+_input$', i)
    ]
    code_input_form_name.sort()
    if len(code_input_form_name) == 0:
      print(self, "授業なし")
      return
    for i in range(4):
      values["data"][code_input_form_name[i]] = code[i]
    self.update_soup(**values)
    form = self.get_form("pmPage:funcForm")
    if not form.find(None, text="出席"):
      print(self, "出席失敗")
    else:
      print(self, "出席成功")
