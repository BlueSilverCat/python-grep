import os
import os.path
import re
import argparse

# from EntryInfo import EntryInfo
from EntryList import EntryList
from Regex import Regex
import utility

########################################################################################################################
## Grep
########################################################################################################################


class Grep:

  def __init__(self, args):
    self.setSearchOption(args)
    self.setPrintOption(args)
    self.setFlag(args)
    self.compile()
    self.entryList = EntryList(self.path, self.reInclude, self.reExclude)
    self.regex = Regex(self.pattern, self.flags)

  def setSearchOption(self, args):
    self.path = args.path
    self.pattern = args.pattern
    self.repl = args.replace
    self.invertMatch = args.invertMatch
    self.include = args.include
    self.exclude = args.exclude

  def setPrintOption(self, args):
    self.tree = args.tree
    self.noCaption = args.noCaption
    self.noLineNumber = args.noLineNumber
    self.lineNumberLength = args.lineNumberLength
    self.noFileName = args.noFileName
    self.fileNameLength = args.fileNameLength
    self.noOffset = args.noOffset
    self.offsetLength = args.offsetLength
    self.showZeroLength = args.showZeroLength
    self.showOnlyMatch = args.showOnlyMatch
    self.replaceTest = args.replaceTest

  def setFlag(self, args):
    self.flags = 0
    if args.ascii:
      self.flags += re.ASCII
    if args.ignoreCase:
      self.flags += re.IGNORECASE
    if args.multiLine:
      self.flags += re.MULTILINE
    if args.dotAll:
      self.flags += re.DOTALL

  def compile(self):
    self.reInclude = None
    if self.include is not None:
      self.reInclude = re.compile(self.include, flags=self.flags)
    self.reExclude = None
    if self.exclude is not None:
      self.reExclude = re.compile(self.exclude, flags=self.flags)

  def __repr__(self):
    return f"{self.pattern}, {self.flags}, {len(self.regex.matchLineInfo)}"

  def perform(self):
    self.printTree()
    for entryInfo in self.entryList.entries:
      if not entryInfo.isFile():
        continue

      with open(entryInfo.path, "r", encoding="utf-8", newline="") as file:
        data = file.read()
      linebreak = utility.getLineBreak(data)
      self.regex.perform(data, linebreak, self.showZeroLength, self.invertMatch)

      # self.regex.printLineInfo(self.invertMatch)

      if self.showOnlyMatch:
        self.printMessageOnly(entryInfo.name)
      else:
        self.printMessage(entryInfo.name, data, linebreak)
      replaceFlag, data = self.replace(data)
      if replaceFlag:
        if self.replaceTest:
          print(data)
        else:
          self.write(entryInfo.path, data)

  def replace(self, string):
    if self.repl is None:
      return (False, string)

    if not self.invertMatch and len(self.regex.matchInfo) > 0:
      result = self.regex.regex.sub(self.repl, string)
      return (True, result)
    elif self.invertMatch:
      result = self.replaceRange(string)
      return (True, result)
    return (False, string)

  def replaceRange(self, string):
    work = string
    length = len(string)
    for info in self.regex.matchInfo:
      diff = len(work) - length
      work = work[:info.start + diff] + self.repl + work[info.end + diff:]
    return work

  ## print

  def printTree(self):
    if not self.tree:
      return
    self.entryList.printTree()

  def printCaption(self, name):
    if not self.noCaption:
      print(f"# {name} #")

  def getFileName(self, name):
    return f"{name:{self.fileNameLength}}" if not self.noFileName else ""

  def getLineNumber(self, info):
    return f"[{info.line:0{self.lineNumberLength}}]" if not self.noLineNumber else ""

  def getOffset(self, info):
    return f"({info.start:0{self.offsetLength}}:{info.length:0{self.offsetLength}})" if not self.noOffset else ""

  def getSeparetor(self):
    return f":" if not self.noFileName or not self.noLineNumber or not self.noOffset else ""

  # 一致した文字列を含む行を出力する
  def printMessage(self, name, text, linebreak="\n", replacer=""):  # replacer="↲"
    if len(self.regex.matchLineInfo) <= 0:
      return
    self.printCaption(name)
    lineText = utility.split(text, linebreak, replacer)
    previousLine = -1
    string = ""
    offsetString = ""
    for info in self.regex.matchLineInfo:
      if info.line != previousLine and previousLine > -1:
        print(string)
        offsetString = ""
        string = ""
      string = self.getFileName(name)
      string += self.getLineNumber(info)
      offsetString = offsetString + self.getOffset(info)
      if not self.noOffset:
        string += f"{offsetString}"
      string += self.getSeparetor()
      string += f"{lineText[info.line]}"
      previousLine = info.line
    print(string)

  # 一致文字だけを出力する
  def printMessageOnly(self, name, linebreak="\n", replacer=""):  # replacer="↲"
    if len(self.regex.matchLineInfo) <= 0:
      return
    self.printCaption(name)
    string = ""
    for info in self.regex.matchLineInfo:
      string = self.getFileName(name)
      string += self.getLineNumber(info)
      string += self.getOffset(info)
      string += self.getSeparetor()
      string += f"{info.string.replace(linebreak, replacer)}"
      print(string)

  @staticmethod
  def write(path, string):
    with open(path, "w", encoding="utf-8", newline="") as file:  # 改行コード
      file.write(string)


########################################################################################################################
## argument
########################################################################################################################

# flags
# re.ASCII
# re.DEBUG: 無効
# re.IGNORECASE
# re.MULTILINE
# re.DOTALL:
# re.VERBOSE: 無効


def argumentParser():
  parser = argparse.ArgumentParser()
  # search option
  parser.add_argument("path", help="specify file or directory.")
  parser.add_argument("pattern", help="specify search string as regular expression.")
  parser.add_argument("-r",
                      "--replace",
                      nargs="?",
                      const="",
                      help="specify replace string. replace matching strings with this string.")  # 空文字列を受け取れる設定
  parser.add_argument("-rt", "--replaceTest", action="store_true", help="Show only the result of replacement.")
  parser.add_argument("-v", "--invertMatch", action="store_true", help="select non-matching lines.")
  parser.add_argument("-i", "--include", help="search only path that match pattern.")
  parser.add_argument("-e", "--exclude", help="skip path match pattern.")

  # match option
  parser.add_argument(
      "-A",
      "--ascii",
      action="store_true",
      help="make \\w, \\W, \\b, \\B, \\d, \\D, \\s and \\S perform ASCII-only matching instead of full Unicode matching."
  )
  parser.add_argument("-I", "--ignoreCase", action="store_true", help="perform case-insensitive matching.")
  parser.add_argument(
      "-M",
      "--multiLine",
      action="store_true",
      help=
      "when specified, the pattern character '^' matches at the beginning of the string and at the beginning of each line (immediately following each newline)."
  )
  parser.add_argument("-D",
                      "--dotAll",
                      action="store_true",
                      help="make the '.' special character match any character at all, including a newline.")

  # tree view
  parser.add_argument("-t", "--tree", action="store_true", help="show directory tree.")

  # printOption
  parser.add_argument("-a", "--showArgument", action="store_true", help="show arguments.")
  parser.add_argument("-c", "--noCaption", action="store_true", help="no print file name as caption.")
  parser.add_argument("-l", "--noLineNumber", action="store_true", help="no print line number with output lines.")
  parser.add_argument("-ll", "--lineNumberLength", type=int, default=4, help="line number length.")
  parser.add_argument("-f", "--noFileName", action="store_true", help="no print file name with output lines.")
  parser.add_argument("-fl", "--fileNameLength", type=int, default=1, help="file name length.")
  parser.add_argument("-o", "--noOffset", action="store_true", help="no print offset with output lines.")
  parser.add_argument("-ol", "--offsetLength", type=int, default=3, help="offset length.")
  parser.add_argument("-z", "--showZeroLength", action="store_true", help="show zero length match.")
  parser.add_argument("-O", "--showOnlyMatch", action="store_true", help="show only matched strings.")
  return parser.parse_args()


########################################################################################################################
## main
########################################################################################################################

if __name__ == "__main__":
  args = argumentParser()
  if args.showArgument:
    print(args)

  grep = Grep(args)
  grep.perform()
