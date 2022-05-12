import requests
import re
from urllib.parse import urlencode
from bs4 import BeautifulSoup, Tag

class UnipaMobail:
  HOST = "https://unipa.i-u.ac.jp"
  def __init__(self, user_id, user_paswrd):
    self.session = requests.session()
    self.user_id = user_id
    self.user_paswrd = user_paswrd
    self.menu_soup = None
    self.login()
  def get_form(self, soup:BeautifulSoup, name:str):
    return soup.find('form', attrs={"name": name})
  def get_soup(self, path, data=None, certification=True,**kwargs):
    response = self.session.post(
      url = self.HOST + path,
      data = urlencode(data) if data is not None else None,
      **kwargs, 
      )
    soup = BeautifulSoup(response.content, "html.parser")
    self.menu_soup = self.get_form(soup, "pmPage:menuForm")
    if self.menu_soup is None and certification:
      raise Exception("タイムアウト")
    return soup
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
  def login(self):
    soup = self.get_soup(path='/uprx/up/pk/pky501/Pky50101.xhtml', certification=False)
    form = self.get_form(soup, "pmPage:loginForm")
    values = self.formatting(form)
    values["data"]["pmPage:loginForm:userId_input"] = self.user_id
    values["data"]["pmPage:loginForm:password"] = self.user_paswrd
    try:
      self.get_soup(**values)
    except Exception:
      raise Exception("ログインエラー")
    print(self, "ログイン")
  def click_menu(self, num):
    values = self.formatting(self.menu_soup)
    values["data"] = {k:v for k, v in values["data"].items() if "pmPage:menuForm:" not in k}
    values["data"][f"pmPage:menuForm:j_idt37:{num}:menuBtn1"] = ""
    soup = self.get_soup(**values)
    return soup
  def get_attend_form(self):
    soup = self.click_menu(16)
    form = self.get_form(soup, "pmPage:funcForm")
    if form.find(None, text="出席"):
      raise Exception("出席済み")
    elif form.find(None, text="現在、履修している授業はありません。"):
      raise Exception("授業なし")
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
      raise Exception("授業なし")
    return values, code_input_form_name
  def attend(self, attend_form, code):
    if not re.match(r'^\d{4}$', code):
      raise Exception("出席コードエラー")
    values, code_input_form_name = attend_form
    for i in range(4):
      values["data"][code_input_form_name[i]] = code[i]
    soup = self.get_soup(**values)
    form = self.get_form(soup, "pmPage:funcForm")
    if not form.find(None, text="出席"):
      raise Exception("出席失敗")
    else:
      print(self, "出席成功")
  def __repr__(self):
    return f"<UnipaMobail {self.user_id}>"

if __name__ == "__main__":
  user_id = input("ID>>")
  user_paswrd = input("paswrd>>")
  user = UnipaMobail(user_id, user_paswrd)
  attend_form = user.get_attend_form()
  code = input("code>>")
  user.attend(attend_form, code)