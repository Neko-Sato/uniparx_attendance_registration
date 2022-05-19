from __future__ import annotations
from typing import TYPE_CHECKING
from bs4 import BeautifulSoup
import re

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
    self.initialization()
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

# class AttendAction(Action):
#   def __init__(self, unipa):
#       super().__init__(unipa)
#   def initialization(self):
#     self.click_menu("出席登録")
#     self.funcForm = self.unipa.get_form("pmPage:funcForm")
#     if self.funcForm.soup.find(None, text="出席"):
#       raise AttendError("出席済み")
#     elif self.funcForm.soup.find(None, text="出席確認終了"):
#         raise AttendError("欠席")
#     elif self.funcForm.soup.find(None, text="現在、履修している授業はありません。"):
#       raise AttendError("授業なし")
#   def execution(self, code:str):
#     if not re.match(r'^\d{4}$', code):
#       raise AttendError("出席コードエラー")
#     code_inputs = self.funcForm.find_all(re.compile("^.*_input$"))
#     for i, t in enumerate(code_inputs):
#       t.value = code[i]
#     values = self.funcForm.get_request_args(
#       self.funcForm.funs[4],
#       *code_inputs,
#     )
#     self.unipa.update_soup(**values)
#     funcForm = self.unipa.get_form("pmPage:funcForm")
#     if not funcForm.soup.find(None, text="出席"):
#       self.initialization()
#       raise AttendError("出席失敗")
#     super().close()

# class GetAssignmentsAction(Action):
#   def __init__(self, unipa):
#     super().__init__(unipa)
#   def execution(self):
#     result = []
#     for code in self.get_jugyoCodes():
#       self.go_class_profile()

#       funcForm = self.unipa.get_form("pmPage:funcForm")
#       jugyo = funcForm.soup.find("span", class_="jugyoCode", text=code).find_parent("a")
#       button_name = jugyo.attrs["id"]
#       jugyoName = jugyo.find("span", class_="jugyoName").text
#       values = funcForm.get_request_args(
#         funcForm[button_name],
#       )
#       self.unipa.update_soup(**values)

#       funcForm = self.unipa.get_form("pmPage:funcForm")
#       button_name = funcForm.soup.find(text=re.compile("課題提出")).find_parent("a").attrs["id"]
#       values = funcForm.get_request_args(
#         funcForm[button_name],
#       )
#       self.unipa.update_soup(**values)

#       funcForm = self.unipa.get_form("pmPage:funcForm")
#       arg_id = funcForm.soup.find("label", text=re.compile("未提出")).attrs["for"]
#       arg_name = funcForm.soup.find("input", id=arg_id).attrs["name"]
#       button_name = funcForm.soup.find("button", text=re.compile("検索する")).attrs["id"]
#       funcForm["pmPage:funcForm:status"].value = "2"
      
#       values = funcForm.get_request_args(
#         funcForm[button_name],
#         funcForm[arg_name],
#         funcForm["pmPage:funcForm:status"],
#       )
#       self.unipa.update_soup(**values)

#       funcForm = self.unipa.get_form("pmPage:funcForm")
#       listArea = funcForm.soup.find("div", id="pmPage:funcForm:listArea")
#       if listArea is None:
#         continue
#       for i in listArea.find_all("a"):
#         i:BeautifulSoup
#         title = f'{jugyoName} {i.find("span", class_="title").text}'
#         limit = i.find(text="提出開始日時：").next.text
#         result.append((title , limit))
#       super().close()
#       return result
#   def go_class_profile(self):
#     self.click_menu("ポータルトップ(スマートフォン)")
#     funcForm = self.unipa.get_form("pmPage:funcForm")
#     button_name = funcForm.soup.find(text="ｸﾗｽﾌﾟﾛﾌｧｲﾙ").find_parent("a").attrs["id"]
#     values = funcForm.get_request_args(
#       funcForm[button_name],
#     )
#     self.unipa.update_soup(**values)
#   def get_jugyoCodes(self):
#     self.go_class_profile()
#     funcForm = self.unipa.get_form("pmPage:funcForm")
#     return list({i.text for i in funcForm.soup.find_all(class_="jugyoCode")})