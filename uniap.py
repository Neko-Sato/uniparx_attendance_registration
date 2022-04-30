import requests
from urllib.parse import urlencode
from bs4 import BeautifulSoup

CODE = input("code >> ")

USER_ID = input("id >> ")
USER_PASWRD = input("pass >> ")

HOST = "https://unipa.i-u.ac.jp"

def get_form(soup:BeautifulSoup, name:str):
  form = soup.find('form', attrs={"name": name})
  values = [
    *form.find_all("input"),
    *form.find_all("button"),
  ]
  result = {
    "method": form.attrs.get("method"),
    "path": form.attrs.get("action"),
    "headers": {
      "content-type" : form.attrs.get("enctype")
    },
    "data": {
      i.attrs.get("name"): i.attrs.get("value") if i.attrs.get("value") != None else "" 
      for i in values
    },
  }
  return result

session = requests.session()

##ログインに必要なものを集める
response = session.post(HOST + '/uprx/up/pk/pky501/Pky50101.xhtml')
soup = BeautifulSoup(response.content, "html.parser")
data = get_form(soup, "pmPage:loginForm")

##ログインしてトークンらを習得
data["data"]["pmPage:loginForm:userId_input"] = USER_ID
data["data"]["pmPage:loginForm:password"] = USER_PASWRD

response = session.post(
  HOST + data["path"],
  headers = data["headers"],
  data = urlencode(data["data"]),
)
soup = BeautifulSoup(response.content, "html.parser")
data = get_form(soup, "pmPage:menuForm")

##出席コードの画面の取得
data["data"] = dict(filter(lambda item: "pmPage:menuForm:" not in item[0], data["data"].items()))
data["data"]["pmPage:menuForm:j_idt37:16:menuBtn1"] = ""

response = session.post(
  HOST + data["path"],
  headers = data["headers"],
  data = urlencode(data["data"]),
)
soup = BeautifulSoup(response.content, "html.parser")
data = get_form(soup, "pmPage:funcForm")

##出席コードの送信
del data["data"]["pmPage:funcForm:j_idt139"]

n = 0
for i in data["data"].keys():
  if "pmPage:funcForm:j_idt90:" in i:
    t = i[24:]
    n = t[:t.find(":")]
    break
del data["data"][f"pmPage:funcForm:j_idt90:{n}:j_idt95"]
del data["data"][f"pmPage:funcForm:j_idt90:{n}:j_idt94"]
del data["data"][f"pmPage:funcForm:j_idt90:{n}:j_idt93"]

data["data"][f'pmPage:funcForm:j_idt90:{n}:j_idt101_input'] = CODE[0]
data["data"][f'pmPage:funcForm:j_idt90:{n}:j_idt102_input'] = CODE[1]
data["data"][f'pmPage:funcForm:j_idt90:{n}:j_idt103_input'] = CODE[2]
data["data"][f'pmPage:funcForm:j_idt90:{n}:j_idt104_input'] = CODE[3]

response = session.post(
  HOST + data["path"],
  headers = data["headers"],
  data = urlencode(data["data"]),
)
soup = BeautifulSoup(response.content, "html.parser")
