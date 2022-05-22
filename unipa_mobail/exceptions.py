class FormNotFound(Exception):
  pass

class ActionError(Exception):
  pass

class UnipaError(Exception):
  def __init__(self, massgae):
    self.massgae = massgae

class LoginError(UnipaError):
  def __init__(self):
    super().__init__("ログインエラー")

class MaintenanceError(UnipaError):
  def __init__(self):
    super().__init__("メンテナンス中です")

class TimeoutError(UnipaError):
  def __init__(self):
    super().__init__("タイムアウト")

