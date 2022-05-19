from unipa_mobail import *
from unipa_actions import AttendAction

user_id = input("id>>")
user_paswrd = input("paswrd>>")
user = UnipaMobail(user_id, user_paswrd)
with AttendAction(user) as action:
  code = input("code>>")
  action.execution(code)