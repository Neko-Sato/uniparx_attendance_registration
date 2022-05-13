from attend_unipa import *
import tkinter as tk
import configparser
import os

class UnipaMobailController:
  def __init__(self):
    self.user = None
    self.config_path = os.path.join(os.path.expanduser("~"), "attend_unipa.config")
    self.config = configparser.ConfigParser()
    self.config.read(self.config_path)
    self.config.setdefault('Certification', {"id": "", "paswrd": ""})
    self.relogin()
  def relogin(self):
    if not self.config.get('Certification', "id") == "":
      try:
        self.login(
          self.config.get('Certification', "id"), 
          self.config.get('Certification', "paswrd")
        )
      except Exception:
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

class App(tk.Tk):
  def __init__(self):
    super().__init__()
    self.current_page = None
  def display(self, page:tk.Frame):
    if self.current_page is not None:
      self.current_page.destroy()
    page.pack()
    self.current_page = page

class AttendUnipa(App):
  def __init__(self):
    super().__init__()
    self.title("うにぱしゅっせき")
    self.controller = UnipaMobailController()
    self.resizable(width=False, height=False)
    self.logout_button = tk.Button(self, text="ログアウト", command=self.logout)
    if self.controller.user is None:
      self.display(LoginPage(self))
    else:
      self.logout_button.pack()
      self.display(Home(self))
  def login(self, user_id, user_paswrd):
    self.controller.login(user_id, user_paswrd)
    self.logout_button.pack()
    self.display(Home(self))
  def logout(self):
    self.controller.logout()
    self.logout_button.pack_forget()
    self.display(LoginPage(self))
  def get_attend_form(self):
    return self.controller.user.get_attend_form()
  def attend(self, attend_form, code):
    try:
      self.controller.user.attend(attend_form, code)
      page = ResultPage(self, "出席成功")
    except Exception as e:
      page = ResultPage(self, e.args[0])
      if e.args[0] == "タイムアウト":
        self.controller.relogin()
        if self.controller.user is None:
          page = LoginPage(self)
          
    self.display(page)

class UnipaPage(tk.Frame):
  def __init__(self, unipa:AttendUnipa):
    super().__init__(unipa)
    self.unipa:AttendUnipa = unipa

class LoginPage(UnipaPage):
  def __init__(self, unipa):
    super().__init__(unipa)
    
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
      self.unipa.login(self.id_input.get(), self.paswrd_input.get())
    except Exception:
      self.error_massage.grid()

class Home(UnipaPage):
  def __new__(cls, unipa):
    try:
      attend_form = unipa.get_attend_form()
      return AttendPage(unipa, attend_form)
    except Exception as e:
      return ResultPage(unipa, e.args[0])

class AttendPage(UnipaPage):
  def __init__(self, unipa, attend_form):
    super().__init__(unipa)
    self.unipa = unipa
    self.attend_form = attend_form

    self.title = tk.Label(self, text="出席コード入力")
    self.title.grid(column=0, row=0, padx=5, pady=5)

    self.code_input = tk.Entry(self)
    self.code_input.focus_set()
    self.code_input.bind("<Key-Return>", lambda _: self.send())
    self.code_input.grid(column=0, row=1, padx=5, pady=5)

    self.send_button = tk.Button(self, text="送信", command=self.send)
    self.send_button.grid(column=0, row=2, padx=5, pady=5)
  def send(self):
    self.unipa.attend(self.attend_form, self.code_input.get())

class ResultPage(UnipaPage):
  def __init__(self, unipa, massage):
    super().__init__(unipa)
    self.unipa = unipa
    
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
    self.unipa.destroy()
  def retry(self):
    self.unipa.display(Home(self.unipa))

if __name__ == "__main__":
  AttendUnipa().mainloop()
