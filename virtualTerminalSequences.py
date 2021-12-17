from ctypes import windll, wintypes, byref
from functools import reduce


class VirtualTerminalSequences:
  RESET = "\x1b[0m"  # reset
  BOLD = "\x1b[1m"
  UNDERLINE = "\x1b[4m"
  REVERSE = "\x1b[07m"  # reverse foreground and background colors
  UNDERLINE_OFF = "\x1b[24m"
  REVERSE_OFF = "\x1b[27m"
  FOREGROUND_COLORS = {
    "BLACK": "\x1b[30m",
    "RED": "\x1b[31m",
    "GREEN": "\x1b[32m",
    "YELLOW": "\x1b[33m",
    "BLUE": "\x1b[34m",
    "MAGENTA": "\x1b[35m",
    "CYAN": "\x1b[36m",
    "WHITE": "\x1b[37m",
    "DEFAULT_COLOR": "\x1b[39m",
    "GRAY": "\x1b[90m",
    "BRIGHT_RED": "\x1b[91m",
    "BRIGHT_GREEN": "\x1b[92m",
    "BRIGHT_YELLOW": "\x1b[93m",
    "BRIGHT_BLUE": "\x1b[94m",
    "BRIGHT_MAGENTA": "\x1b[95m",
    "BRIGHT_CYAN": "\x1b[96m",
    "BRIGHT_WHITE": "\x1b[97m",
  }
  BACKGROUND_COLORS = {
    "BLACK": "\x1b[40m",
    "RED": "\x1b[41m",
    "GREEN": "\x1b[42m",
    "YELLOW": "\x1b[43m",
    "BLUE": "\x1b[44m",
    "MAGENTA": "\x1b[45m",
    "CYAN": "\x1b[46m",
    "WHITE": "\x1b[47m",
    "DEFAULT_COLOR": "\x1b[49m",
    "GRAY": "\x1b[100m",
    "BRIGHT_RED": "\x1b[101m",
    "BRIGHT_GREEN": "\x1b[102m",
    "BRIGHT_YELLOW": "\x1b[103m",
    "BRIGHT_BLUE": "\x1b[104m",
    "BRIGHT_MAGENTA": "\x1b[105m",
    "BRIGHT_CYAN": "\x1b[106m",
    "BRIGHT_WHITE": "\x1b[107m",
  }

  INVALID_HANDLE_VALUE = -1
  STD_OUTPUT_HANDLE = -11
  STD_ERROR_HANDLE = -12
  ENABLE_VIRTUAL_TERMINAL_PROCESSING = 0x0004
  ENABLE_LVB_GRID_WORLDWIDE = 0x0010

  @staticmethod
  def enable():
    hOut = windll.kernel32.GetStdHandle(VirtualTerminalSequences.STD_OUTPUT_HANDLE)
    if hOut == VirtualTerminalSequences.INVALID_HANDLE_VALUE:
      return False
    dwMode = wintypes.DWORD()
    if windll.kernel32.GetConsoleMode(hOut, byref(dwMode)) == 0:
      return False
    dwMode.value |= VirtualTerminalSequences.ENABLE_VIRTUAL_TERMINAL_PROCESSING
    # dwMode.value |= ENABLE_LVB_GRID_WORLDWIDE
    if windll.kernel32.SetConsoleMode(hOut, dwMode) == 0:
      return False
    return True

  @staticmethod
  def reset():
    print(VirtualTerminalSequences.RESET)

  @staticmethod
  def getForegroundColor(name="BLACK"):
    name = name.upper()
    try:
      return VirtualTerminalSequences.FOREGROUND_COLORS[name]
    except:
      return ""

  @staticmethod
  def getBackgroundColor(name="BLACK"):
    name = name.upper()
    try:
      return VirtualTerminalSequences.BACKGROUND_COLORS[name]
    except:
      return ""

  @staticmethod
  def getForegroundColorN(n):
    if n >= 0 and n <= 255:
      return f"\x1b[38;5;{n}m"
    return VirtualTerminalSequences.FOREGROUND_COLORS["DEFAULT_COLOR"]

  @staticmethod
  def getForegroundColorRGB(r, g, b):
    if r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255:
      return f"\x1b[38;2;{r};{g};{b}m"
    return VirtualTerminalSequences.FOREGROUND_COLORS["DEFAULT_COLOR"]

  @staticmethod
  def getBackgroundColorN(n):
    if n >= 0 and n <= 255:
      return f"\x1b[48;5;{n}m"
    return VirtualTerminalSequences.BACKGROUND_COLORS["DEFAULT_COLOR"]

  @staticmethod
  def getBackgroundColorRGB(r, g, b):
    if r >= 0 and r <= 255 and g >= 0 and g <= 255 and b >= 0 and b <= 255:
      return f"\x1b[48;2;{r};{g};{b}m"
    return VirtualTerminalSequences.BACKGROUND_COLORS["DEFAULT_COLOR"]

  @staticmethod
  def getColorMessage(msg, foreground="", background="", reset=True):
    msg = f"{VirtualTerminalSequences.getForegroundColor(foreground)}{VirtualTerminalSequences.getBackgroundColor(background)}{msg}"
    if reset == False:
      return msg
    return f"{msg}{VirtualTerminalSequences.RESET}"

  @staticmethod
  def getColorMessageN(msg, foreground=-1, background=-1, reset=True):
    msg = f"{VirtualTerminalSequences.getForegroundColorN(foreground)}{VirtualTerminalSequences.getBackgroundColorN(background)}{msg}"
    if reset == False:
      return msg
    return f"{msg}{VirtualTerminalSequences.RESET}"

  @staticmethod
  def getColorMessageRGB(msg, foreground=(-1, -1, -1), background=(-1, -1, -1), reset=True):
    msg = f"{VirtualTerminalSequences.getForegroundColorRGB(*foreground)}{VirtualTerminalSequences.getBackgroundColorRGB(*background)}{msg}"
    if reset == False:
      return msg
    return f"{msg}{VirtualTerminalSequences.RESET}"

  @staticmethod
  def getBoldMessage(msg, reset=True):
    msg = f"{VirtualTerminalSequences.BOLD}{msg}"
    if reset == False:
      return msg
    return f"{msg}{VirtualTerminalSequences.RESET}"

  @staticmethod
  def getUnderlineMessage(msg, reset=True):
    msg = f"{VirtualTerminalSequences.UNDERLINE}{msg}"
    if reset == False:
      return msg
    return f"{msg}{VirtualTerminalSequences.RESET}"

  @staticmethod
  def getReverseMessage(msg, reset=True):
    msg = f"{VirtualTerminalSequences.REVERSE}{msg}"
    if reset == False:
      return msg
    return f"{msg}{VirtualTerminalSequences.RESET}"
