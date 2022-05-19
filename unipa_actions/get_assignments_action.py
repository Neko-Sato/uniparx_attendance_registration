import re
from bs4 import BeautifulSoup
from unipa_mobail import Action

class GetAssignmentsAction(Action):
  def execution(self):
    result = []
    for code in self.get_jugyoCodes():
      self.go_class_profile()

      funcForm = self.unipa.get_form("pmPage:funcForm")
      jugyo = funcForm.soup.find("span", class_="jugyoCode", text=code).find_parent("a")
      button_name = jugyo.attrs["id"]
      jugyoName = jugyo.find("span", class_="jugyoName").text
      values = funcForm.get_request_args(
        funcForm[button_name],
      )
      self.unipa.update_soup(**values)

      funcForm = self.unipa.get_form("pmPage:funcForm")
      button_name = funcForm.soup.find(text=re.compile("課題提出")).find_parent("a").attrs["id"]
      values = funcForm.get_request_args(
        funcForm[button_name],
      )
      self.unipa.update_soup(**values)

      funcForm = self.unipa.get_form("pmPage:funcForm")
      arg_id = funcForm.soup.find("label", text=re.compile("未提出")).attrs["for"]
      arg_name = funcForm.soup.find("input", id=arg_id).attrs["name"]
      button_name = funcForm.soup.find("button", text=re.compile("検索する")).attrs["id"]
      funcForm["pmPage:funcForm:status"].value = "2"
      
      values = funcForm.get_request_args(
        funcForm[button_name],
        funcForm[arg_name],
        funcForm["pmPage:funcForm:status"],
      )
      self.unipa.update_soup(**values)

      funcForm = self.unipa.get_form("pmPage:funcForm")
      listArea = funcForm.soup.find("div", id="pmPage:funcForm:listArea")
      if listArea is None:
        continue
      for i in listArea.find_all("a"):
        i:BeautifulSoup
        title = f'{jugyoName} {i.find("span", class_="title").text}'
        limit = i.find(text="提出開始日時：").next.text
        result.append((title , limit))
    return result
  @Action.deco_only_execution
  def go_class_profile(self):
    self.click_menu("ポータルトップ(スマートフォン)")
    funcForm = self.unipa.get_form("pmPage:funcForm")
    button_name = funcForm.soup.find(text="ｸﾗｽﾌﾟﾛﾌｧｲﾙ").find_parent("a").attrs["id"]
    values = funcForm.get_request_args(
      funcForm[button_name],
    )
    self.unipa.update_soup(**values)
  @Action.deco_only_execution
  def get_jugyoCodes(self):
    self.go_class_profile()
    funcForm = self.unipa.get_form("pmPage:funcForm")
    return list({i.text for i in funcForm.soup.find_all(class_="jugyoCode")})