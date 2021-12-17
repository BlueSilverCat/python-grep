import logging
import logging.handlers
import sys
from virtualTerminalSequences import VirtualTerminalSequences as VTS


class LevelFilter(logging.Filter):  # 特定levelだけを通過させるフィルタ

  def __init__(self, level=logging.INFO):
    super().__init__()
    self.level = level

  def filter(self, record):
    if record.levelno != self.level:
      return False  # Falseを返すとrecordの走査が止まるので見つけ次第Falseを返すと良い
    return True


class ColorFilter(logging.Filter):

  def __init__(self):
    super().__init__()
    VTS.enable()

  def filter(self, record):
    if record.levelno == logging.DEBUG:
      record.msg = VTS.getColorMessage(record.msg, "green")
    if record.levelno == logging.INFO:
      record.msg = VTS.getColorMessage(record.msg, "cyan")
    if record.levelno == logging.WARNING:
      record.msg = VTS.getColorMessage(record.msg, "yellow")
    if record.levelno == logging.ERROR:
      record.msg = VTS.getColorMessage(record.msg, "magenta")
    if record.levelno == logging.CRITICAL:
      record.msg = VTS.getColorMessage(record.msg, "red")
    return True
