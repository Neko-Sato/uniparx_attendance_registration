import re
from unipa_mobail import Action, UnipaError

class AttendAction(Action):
  def initialization(self):
    self.click_menu("出席登録")
    self.funcForm = self.unipa.get_form("pmPage:funcForm")
    if self.funcForm.soup.find(None, text="出席"):
      raise AttendError("出席済み")
    elif self.funcForm.soup.find(None, text="出席確認終了"):
        raise AttendError("欠席")
    elif self.funcForm.soup.find(None, text="現在、履修している授業はありません。"):
      raise AttendError("授業なし")
  def execution(self, code:str):
    if not re.match(r'^\d{4}$', code):
      raise AttendError("出席コードエラー")
    code_inputs = self.funcForm.find_all(re.compile("^.*_input$"))
    for i, t in enumerate(code_inputs):
      t.value = code[i]
    values = self.funcForm.get_request_args(
      self.funcForm.funs[4],
      *code_inputs,
    )
    self.unipa.update_soup(**values)
    funcForm = self.unipa.get_form("pmPage:funcForm")
    if not funcForm.soup.find(None, text="出席"):
      self.initialization()
      raise AttendError("出席失敗")

class AttendError(UnipaError):
  pass