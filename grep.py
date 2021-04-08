import os
import os.path
import re
import argparse

########################################################################################################################
## EntryInfo
########################################################################################################################


class EntryInfo():

  def __init__(self, path, depth=0):
    if not os.path.exists(path):
      print(path)
      raise ValueError
    self.path = os.path.abspath(path)
    self.name = os.path.basename(self.path)
    self.depth = depth
    self.setAttribute()

  def __str__(self):
    # return f"{'  ' * self.depth}{self.attribute}: {self.name}"
    return f"{self.attribute}: {self.name}"

  def __lt__(self, other):
    if self.attribute == other.attribute:
      return self.name > other.name
    else:
      return EntryInfo.getAttributePriority(self.attribute) > EntryInfo.getAttributePriority(other.attribute)

  def getOutputString(self):
    return f"{'  ' * self.depth}{str(self)}"

  def setAttribute(self):
    self.attribute = ""
    if os.path.isdir(self.path):  # True: file or dirLink
      self.attribute = "d"
    elif os.path.isfile(self.path):  # True: file or fileLink
      self.attribute = "f"
    if os.path.islink(self.path):
      self.attribute += "l"
    else:
      self.attribute += " "

  def isDir(self):
    return True if "d" in self.attribute else False

  def isFile(self):
    return True if "f" in self.attribute else False

  def isLink(self):
    return True if "l" in self.attribute else False

  def getStats(self):
    return os.stat(self.path)

  @staticmethod
  def getAttributePriority(attribute):
    if attribute == "f ":
      return 3
    elif attribute == "fl":
      return 4
    elif attribute == "d ":
      return 1
    elif attribute == "dl":
      return 2
    else:
      return 0

  @staticmethod
  def getSubEntries(path, stack, depth=0):
    lt = os.listdir(path)  # オブジェクトの型の問題で os.scandir(path) は使わないことにした
    entries = []
    for i in lt:
      entries.append(EntryInfo(os.path.join(path, i), depth))
    entries.sort()
    stack += entries

  @staticmethod
  def filterEntries(entries, reInclude=None, reExclude=None):
    result = []
    for entry in entries:
      if reInclude is not None and reInclude.search(entry.path) is None:
        continue
      if reExclude is not None and reExclude.search(entry.path) is not None:
        continue
      result.append(entry)
    return result

  @staticmethod
  def printTree(entries):
    for entry in entries:
      print(entry.getOutputString())


########################################################################################################################
## grep
########################################################################################################################


class Grep():

  def __init__(self, args):
    self.linebreak = ""
    self.setSearchOption(args)
    self.setPrintOption(args)
    self.setFlag(args)
    self.compile()

  def setSearchOption(self, args):
    self.path = args.path
    self.search = args.search
    self.repl = args.replace
    self.invertMatch = args.invertMatch
    self.include = args.include
    self.exclude = args.exclude

  def setFlag(self, args):
    self.flags = 0
    if args.ascii:
      self.flags += re.ASCII
    if args.ignoreCase:
      self.flags += re.IGNORECASE
    # if args.multiLine:
    #   self.flags += re.MULTILINE
    if args.dotAll:
      self.flags += re.DOTALL

  def compile(self):
    self.reInclude = None
    if self.include is not None:
      self.reInclude = re.compile(self.include, flags=self.flags)
    self.reExclude = None
    if self.exclude is not None:
      self.reExclude = re.compile(self.exclude, flags=self.flags)
    self.reSearch = re.compile(self.search, flags=self.flags)

  def setPrintOption(self, args):
    self.noCaption = args.noCaption
    self.noLineNumber = args.noLineNumber
    self.lineNumberLength = args.lineNumberLength
    self.noFileName = args.noFileName
    self.fileNameLength = args.fileNameLength
    self.noOffset = args.noOffset
    self.offsetLength = args.offsetLength
    self.showZeroLength = args.showZeroLength

  def getAllEntries(self):
    self.entryList = [EntryInfo(self.path)]
    if self.entryList[0].isFile():
      return

    workStack = []
    EntryInfo.getSubEntries(self.path, workStack, 1)
    while len(workStack) > 0:
      entry = workStack.pop()
      self.entryList.append(entry)
      if entry.isDir():
        EntryInfo.getSubEntries(entry.path, workStack, entry.depth + 1)

  def scanLines(self, entryInfo):
    line = 0
    replaceFlag = False
    with open(entryInfo.path, "r", encoding="utf-8", newline="") as file:
      data = file.readlines()
      self.printCaption(entryInfo.name)

      for line, text in enumerate(data):
        if line != len(data) -1: # 改行を削除しないと処理がVScodeなどで置換した場合と異なってしまう。最終行は改行を消してしまうと処理がおかしくなる
          text, linebreak = Grep.removeLineBreak(text)

        matchList = search(self.reSearch, text, self.showZeroLength)
        if ((len(matchList) > 0 and not self.invertMatch) or (len(matchList) <= 0 and self.invertMatch)):
          self.printMessage(entryInfo.name, line, text, matchList)

        flag = self.replace(data, line, text)
        if flag:
          replaceFlag = flag
        if line != len(data) -1:
          data[line] += linebreak
    return data if replaceFlag else []

  def replace(self, data, line, text):
    if self.repl is None:
      return False

    if not self.invertMatch and self.reSearch.search(text) is not None:
      data[line] = self.reSearch.sub(self.repl, text)
      return True
    elif self.invertMatch and self.reSearch.search(text) is None:
      data[line] = self.repl
      return True
    return False

  ########################################################################################################################
  ## print
  ########################################################################################################################

  def printTree(self):
    if not self.printTree:
      return
    EntryInfo.printTree(self.entryList)

  def printCaption(self, name):
    if not self.noCaption:
      print(f"# {name} #")

  def printMessage(self, name, line, text, matchList):
    string = ""
    if not self.noFileName:
      string = f"{name:{self.fileNameLength}}"
    if not self.noLineNumber:
      string += f"[{line:0{self.lineNumberLength}}]"
    if not self.noOffset:
      for match in matchList:
        string += f"({match['start']:0{self.offsetLength}}--{match['end']:0{self.offsetLength}}:{match['length']})"
    if not self.noFileName or not self.noLineNumber or not self.noOffset:
      string += f":"
    text, _ = Grep.removeLineBreak(text)
    string += f"{text}"
    print(string)

  @staticmethod
  def writeLines(entryInfo, data):
    if len(data) == 0:
      return
    with open(entryInfo.path, "w", encoding="utf-8", newline="") as file:  # 改行コード
      file.writelines(data)

  @staticmethod
  def removeLineBreak(string):
    linebreak = checkTailLineBreak(string)
    string = removeLineBreak(string, linebreak)
    return (string, linebreak)

########################################################################################################################
## utility
########################################################################################################################


def removeAllLineBreak(string, repl=""):
  reLF = re.compile("\n")
  reCR = re.compile("\r")
  string = reLF.sub(repl, string)
  string = reCR.sub("", string)
  return string


def removeLineBreak(string, linebreak="\n"):
  return string.rstrip(linebreak)


def checkTailLineBreak(string):
  if string.endswith("\r\n"):
    return "\r\n"
  if string.endswith("\n"):
    return "\n"
  return ""


########################################################################################################################
## regex
########################################################################################################################


def search(regex, text, includeZero=False):
  match = regex.search(text)
  if match is None:
    return []

  lt = [getMatchInfo(match)]
  lastIndex = getLastIndex(match)
  while len(text[lastIndex:]) > 0:
    match = regex.search(text[lastIndex:])
    if match is None:
      return lt
    lt.append(getMatchInfo(match, lastIndex))
    lastIndex = getLastIndex(match, lastIndex)
  return lt

def getMatchInfo(match, lastIndex=0):
    start = match.start() + lastIndex
    end = match.end() + lastIndex
    length = len(match[0])
    return {"start": start, "end": end, "length": length, "string": match[0]}

def getLastIndex(match, lastIndex=0):
  end = match.end() + lastIndex
  length = len(match[0])
  return end if length > 0 else end  + 1

########################################################################################################################
## argument
########################################################################################################################

# flags
# re.ASCII
# re.DEBUG: 無効
# re.IGNORECASE
# re.MULTILINE: 無効
# re.DOTALL: 行ごとの処理になっているのであまり有効でない
# re.VERBOSE: 無効


def argumentParser():
  parser = argparse.ArgumentParser()
  # search option
  parser.add_argument("path", help="specify file or directory.")
  parser.add_argument("search", help="specify search string as regular expression.")
  parser.add_argument("-r", "--replace", nargs="?", const="", help="specify replace string.")  # 空文字列を受け取れる設定
  parser.add_argument("-v", "--invertMatch", action="store_true", help="select non-matching lines.")
  parser.add_argument("-i", "--include", help="search only path that match pattern.")
  parser.add_argument("-e", "--exclude", help="skip path match pattern.")

  # match option
  parser.add_argument(
      "-A", "--ascii", action="store_true",
      help="make \\w, \\W, \\b, \\B, \\d, \\D, \\s and \\S perform ASCII-only matching instead of full Unicode matching."
  )
  parser.add_argument("-I", "--ignoreCase", action="store_true", help="perform case-insensitive matching.")
  # parser.add_argument("-m", "--multiLine", action="store_true", help="when specified, the pattern character '^' matches at the beginning of the string and at the beginning of each line (immediately following each newline).")
  parser.add_argument("-D", "--dotAll", action="store_true",
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
  parser.add_argument("-z", "--showZeroLength", action="store_true", help="show zero length match.")  ## fix
  return parser.parse_args()


########################################################################################################################
## main
########################################################################################################################

if __name__ == "__main__":
  args = argumentParser()
  if args.showArgument:
    print(args)

  grep = Grep(args)
  grep.getAllEntries()
  grep.printTree()
  grep.entryList = EntryInfo.filterEntries(grep.entryList, grep.reInclude, grep.reExclude)

  for i in grep.entryList:
    if not i.isFile():
      continue
    data = grep.scanLines(i)
    Grep.writeLines(i, data)
