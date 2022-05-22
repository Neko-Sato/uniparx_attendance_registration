from unipa_mobail import *
from unipa_actions import GetAssignmentsAction

user_id = input("id>>")
user_paswrd = input("paswrd>>")
user = UnipaMobail(user_id, user_paswrd)
with GetAssignmentsAction(user) as action:
  print(action.execution())
