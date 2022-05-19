class FormNotFound(Exception):
  pass

class UnipaError(Exception):
  pass

class LoginError(UnipaError):
  pass

class MaintenanceError(UnipaError):
  pass

class TimeoutError(UnipaError):
  pass

class ActionError(UnipaError):
  pass

