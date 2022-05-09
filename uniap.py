import requests
import re
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
data["data"]["pmPage:loginForm:userId_input"] = USER_ID
data["data"]["pmPage:loginForm:password"] = USER_PASWRD

##ログインしてトークンらを習得
response = session.post(
  HOST + data["path"],
  headers = data["headers"],
  data = urlencode(data["data"]),
)
soup = BeautifulSoup(response.content, "html.parser")

data = get_form(soup, "pmPage:menuForm")
data["data"] = dict(filter(lambda item: "pmPage:menuForm:" not in item[0], data["data"].items()))
data["data"]["pmPage:menuForm:j_idt37:16:menuBtn1"] = ""

##出席コードの画面の取得
response = session.post(
  HOST + data["path"],
  headers = data["headers"],
  data = urlencode(data["data"]),
)
soup = BeautifulSoup(response.content, "html.parser")

data = get_form(soup, "pmPage:funcForm")

del data["data"]["pmPage:funcForm:j_idt139"]
data["data"] = { 
  k : v
  for k, v in data["data"].items()
  if not re.match(r'^pmPage:funcForm:j_idt90:\d+:j_idt(95|94|93)$', k)
  }

code_input_form_name = [
  i
  for i in data["data"].keys() 
  if re.match(r'^pmPage:funcForm:j_idt90:\d+:j_idt\d+_input$', i)
]
code_input_form_name.sort()

for i in range(4):
  data["data"][code_input_form_name[i]] = CODE[i]

##出席コードの送信
response = session.post(
  HOST + data["path"],
  headers = data["headers"],
  data = urlencode(data["data"]),
)
soup = BeautifulSoup(response.content, "html.parser")
# print(soup)
