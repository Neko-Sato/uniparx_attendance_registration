from typing import Optional
import tkinter as tk
from page_app import App, Screen, Page
from page_app.page import LabelPage
from unipa_actions.attend_action import AttendError
from unipa_mobail import UnipaMobail, LoginError, MaintenanceError
from unipa_actions import AttendAction
import configparser
import os

class UnipaAppController:
  user:Optional[UnipaMobail]
  config_path:str
  def __init__(self) -> None:
    self.user = None
    self.config_path = os.path.join(os.path.expanduser("~"), "attend_unipa.config")
    self.config = configparser.ConfigParser()
    self.config.read(self.config_path)
    self.config.setdefault('Certification', {"id": "", "paswrd": ""})
  def relogin(self):
    if not self.config.get('Certification', "id") == "":
      try:
        self.login(
          self.config.get('Certification', "id"), 
          self.config.get('Certification', "paswrd")
        )
      except LoginError:
        self.logout()
  def login(self, user_id, user_paswrd):
    self.user = UnipaMobail(user_id, user_paswrd)
    self.config.set('Certification', "id", user_id)
    self.config.set('Certification', "paswrd", user_paswrd)
    self.set_config()
  def logout(self):
    self.user = None
    self.config.set('Certification', "id", "")
    self.config.set('Certification', "paswrd", "")
    self.set_config()
  def set_config(self):
      with open(self.config_path, 'w') as config_file:
        self.config.write(config_file)

class AttendApp(App):
  def __init__(self) -> None:
    super().__init__()
    self.controller = UnipaAppController()
    self.title("うにぱしゅっせき")
    self.resizable(width=False, height=False)
    self.logout_button = tk.Button(self, text="ログアウト", command=self.logout)
    try:
      self.controller.relogin()
    except MaintenanceError:
      self.screen.display(lambda x: ResultPage(x, "メンテナンス中です"))
    else:
      if self.controller.user is not None:
        self.logout_button.pack()
        self.go_attend_page()
      else:
        self.screen.display(lambda x: LoginPage(x))
  @classmethod
  def of(cls, widget: tk.Widget) -> Optional["AttendApp"]:
    return super().of(widget)
  def login(self, user_id, user_paswrd):
    self.controller.login(user_id, user_paswrd)
    self.logout_button.pack()
    self.go_attend_page()
  def logout(self):
    self.controller.logout()
    self.logout_button.forget()
    self.screen.display(lambda x: LoginPage(x))
  def go_attend_page(self):
    action = AttendAction(self.controller.user)
    try:
      action.open()
      self.screen.display(lambda x: AttendPage(x, action))
    except AttendError as e:
      self.screen.display(lambda x: ResultPage(x, e.massgae))

class LoginPage(Page):
  def __init__(self, screen) -> None:
    super().__init__(screen)
    
    self.title = tk.Label(self, text="ログインフォーム")
    self.title.grid(column=0, row=0, columnspan=2, padx=5, pady=5)

    self.id_label = tk.Label(self, text="ID")
    self.id_label.grid(column=0, row=1, padx=5, pady=0)

    self.id_input = tk.Entry(self)
    self.id_input.focus_set()
    self.id_input.bind("<Key-Return>", lambda _: self.on_key_id_input())
    self.id_input.grid(column=1, row=1, padx=5, pady=0)

    self.paswrd_label = tk.Label(self, text="paswrd")
    self.paswrd_label.grid(column=0, row=2, padx=5, pady=0)

    self.paswrd_input = tk.Entry(self, show='*')
    self.paswrd_input.bind("<Key-Return>", lambda _: self.on_key_paswrd_input())
    self.paswrd_input.grid(column=1, row=2, padx=5, pady=5)

    self.error_massage = tk.Label(self, text="パスワードかIDが間違っています")
    self.error_massage.grid(column=0, row=3, columnspan=2, padx=5, pady=5)
    self.error_massage.grid_remove()

    self.login_button = tk.Button(self, text="ログイン", command=self.on_login)
    self.login_button.bind("<Key-Return>", lambda _: self.on_login())
    self.login_button.grid(column=0, row=4, columnspan=2, padx=5, pady=5)

  def on_key_id_input(self):
    self.paswrd_input.focus_set()
  def on_key_paswrd_input(self):
    self.on_login()
  def on_login(self):
    try:
      AttendApp.of(self).login(self.id_input.get(), self.paswrd_input.get())
    except LoginError:
      self.error_massage.grid()

class AttendPage(Page):
  def __init__(self, screen, action:AttendAction):
    super().__init__(screen)
    self.action = action

    self.title = tk.Label(self, text="出席コード入力")
    self.title.grid(column=0, row=0, padx=5, pady=5)

    self.code_input = tk.Entry(self)
    self.code_input.focus_set()
    self.code_input.bind("<Key-Return>", lambda _: self.send())
    self.code_input.grid(column=0, row=1, padx=5, pady=5)

    self.send_button = tk.Button(self, text="送信", command=self.send)
    self.send_button.grid(column=0, row=2, padx=5, pady=5)
  def send(self):
    self.action.execution(self.code_input.get())
    self.action.close()
    Screen.of(self).display(lambda x: ResultPage(x, "出席成功"))

class ResultPage(Page):
  def __init__(self, screen, massage):
    super().__init__(screen)
    
    self.result_label = tk.Label(self, text=massage)
    self.result_label.grid(column=0, row=0, columnspan=2, padx=5, pady=5)

    self.retry_button = tk.Button(self, text="リトライ", command=self.retry)
    self.retry_button.bind("<Key-Return>", lambda _: self.retry())
    self.retry_button.grid(column=0, row=1, padx=5, pady=5)

    self.close_button = tk.Button(self, text="閉じる", command=self.close)
    self.close_button.bind("<Key-Return>", lambda _: self.close())
    self.close_button.grid(column=1, row=1, padx=5, pady=5)

    if massage in ["出席コードエラー", "出席失敗", "タイムアウト"]:
      self.retry_button.focus_set()
    else:
      self.close_button.focus_set()

  def close(self):
    App.of(self).destroy()
  def retry(self):
    AttendApp.of(self).go_attend_page()

AttendApp().mainloop()