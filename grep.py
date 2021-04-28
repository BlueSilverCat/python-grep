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

  def getIndentedString(self):
    return f"{'  ' * self.depth}{str(self)}"

  @staticmethod
  def getAttribute(path):
    attribute = ""
    if os.path.isdir(path):  # True: file or dirLink
      attribute = "d"
    elif os.path.isfile(path):  # True: file or fileLink
      attribute = "f"
    if os.path.islink(path):
      attribute += "l"
    else:
      attribute += " "
    return attribute

  def setAttribute(self):
    self.attribute = EntryInfo.getAttribute(self.path)

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
      return 1
    elif attribute == "fl":
      return 2
    elif attribute == "d ":
      return 3
    elif attribute == "dl":
      return 4
    else:
      return 0


########################################################################################################################
## EntryList
########################################################################################################################


class EntryList:

  def __init__(self, path, reInclude, reExclude):
    self.entries = []
    self.getAllEntries(path, reInclude, reExclude)

  def getAllEntries(self, path, reInclude, reExclude):
    self.entries = [EntryInfo(path)]
    if self.entries[0].isFile():
      return

    workStack = []
    EntryList.getSubEntries(path, workStack, 1)
    while len(workStack) > 0:
      entry = workStack.pop()
      self.entries.append(entry)
      if entry.isDir():
        EntryList.getSubEntries(entry.path, workStack, entry.depth + 1)
    self.entries = EntryList.filterEntries(self.entries, reInclude, reExclude)

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

  def printTree(self):
    parentList = []
    for i in range(len(self.entries)):
      if self.entries[i].isDir():
        parentList.append(self.entries[i].path)
      parent = os.path.dirname(self.entries[i].path)
      if self.entries[i].isFile() and parent not in parentList and parent != os.path.dirname(self.entries[i - 1].path):
        print(EntryList.getParentName(parent, self.entries[i].depth - 1, parentList))
      print(self.entries[i].getIndentedString())

  @staticmethod
  def getParentName(path, depth, parentList):
    output = ""
    while path not in parentList and depth >= 0:
      name = os.path.basename(path)
      attribute = EntryInfo.getAttribute(path)
      output = f"{'  ' * depth}{attribute}:{name}\n" + output
      parentList.append(path)
      depth -= 1
      path = os.path.dirname(path)
    return output.rstrip()


########################################################################################################################
## MatchLineInfo
########################################################################################################################


class MatchLineInfo:

  def __init__(self, line, start, end, length, string, invert):
    self.line = line
    self.start = start
    self.end = end
    self.length = length
    self.string = string
    self.invert = invert
    # self.setPrintOption()

  def __repr__(self):
    return f"{self.line}: [{self.start}--{self.end}]({self.length})\"{self.string}\" {self.invert}"

  # def setPrintOption(self, noLineNumber=False, lineNumberLength=3, noOffset=False, offsetLength=3, showZeroLength=False, showInvert=False):
  #   self.noLineNumber = noLineNumber
  #   self.lineNumberLength = lineNumberLength
  #   self.noOffset = noOffset
  #   self.offsetLength = offsetLength
  #   self.showZeroLength = showZeroLength
  #   self.showInvert = showInvert


########################################################################################################################
## MatchInfo
########################################################################################################################


class MatchInfo:

  def __init__(self):
    self.start = -1
    self.end = -1
    self.length = -1
    self.string = None
    self.invert = False
    # self.lineInfo = []

  def __repr__(self):
    return f"[{self.start}--{self.end}]({self.length})\"{self.string}\" {self.invert}"

  def __lt__(self, other):
    return self.start < other.start

  def setBasicInfo(self, match, lastIndex=0):
    self.start = match.start() + lastIndex
    self.end = match.end() + lastIndex
    self.string = match[0]
    self.length = len(match[0])
    self.invert = False
    return self

  def setInfo(self, start, end, string, invert=False):
    self.start = start
    self.end = end
    self.string = string
    self.length = len(self.string)
    self.invert = invert
    return self


########################################################################################################################
## grep
########################################################################################################################


class Regex:

  def __init__(self, pattern, flags=0):
    self.pattern = pattern
    self.flags = flags
    self.regex = None
    self.includeZero = True
    # self.string = string
    self.matchInfo = []
    self.matchLineInfo = []
    self.compile()

  def __repr__(self):
    return f"{self.pattern}, {self.flags}, {len(self.matchInfo)}"

  def compile(self):
    self.regex = re.compile(self.pattern, self.flags)

  def search(self, text, includeZero=True):
    self.matchInfo = []
    self.regexInfos = []
    self.includeZero = includeZero
    match = self.regex.search(text)
    if match is None:
      return

    lastIndex = self.storeMatchInfo(match)
    while len(text) >= lastIndex:
      match = self.regex.search(text[lastIndex:])
      if match is None:
        return
      lastIndex = self.storeMatchInfo(match, lastIndex)
    return

  def storeMatchInfo(self, match, lastIndex=0):
    if self.includeZero or len(match[0]) > 0:
      self.matchInfo.append(MatchInfo().setBasicInfo(match, lastIndex))
    return Regex.getLastIndex(match, lastIndex)

  @staticmethod
  def getLastIndex(match, lastIndex=0):
    end = match.end() + lastIndex
    length = len(match[0])
    return end if length > 0 else end + 1

  def setInvert(self, string):
    start = 0
    work = []
    for i in self.matchInfo:
      if i.start > start:
        work.append(MatchInfo().setInfo(start, i.start, string[start:i.start], True))
      start = i.end
    if start < len(string):
      work.append(MatchInfo().setInfo(start, len(string), string[start:], True))
    # self.matchInfo += work
    self.matchInfo = work
    self.matchInfo.sort()

  @staticmethod
  def getLineInfo(string, matchInfo, linebreak="\n"):
    lineInfo = []
    work = matchInfo.string
    matchLines = split(work, linebreak)
    lineOffset = string.count(linebreak, 0, matchInfo.start)
    columnOffset = matchInfo.start - string[:matchInfo.start].rfind(linebreak) - 1
    for i in range(len(matchLines)):
      lineNumber = lineOffset + i
      lineInfo.append(
          MatchLineInfo(line=lineOffset + i,
                        start=columnOffset,
                        end=columnOffset + len(matchLines[i]),
                        length=len(matchLines[i]),
                        string=matchLines[i],
                        invert=matchInfo.invert))
      columnOffset = 0
    return lineInfo

  def setLineInfo(self, string, linebreak="\n"):
    self.matchLineInfo = []
    for i in self.matchInfo:
      for j in Regex.getLineInfo(string, i, linebreak):
        self.matchLineInfo.append(j)

  def printInfo(self, invertMatch=False):
    for i in self.matchInfo:
      if i.invert == invertMatch:
        print(i)

  def printLineInfo(self, invertMatch=False):
    for i in self.matchLineInfo:
      if i.invert == invertMatch:
        print(i)

  def perform(self, data, linebreak="\n", includeZero=True, invertMatch=False):
    self.search(data, includeZero)
    if invertMatch:
      self.setInvert(data)
    self.setLineInfo(data, linebreak)


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
    return f"{self.pattern}, {self.flags}, {len(self.matchInfo)}"

  def perform(self):
    self.printTree()
    for entryInfo in self.entryList.entries:
      if not entryInfo.isFile():
        continue
      self.printCaption(entryInfo.name)
      with open(entryInfo.path, "r", encoding="utf-8", newline="") as file:
        data = file.read()
      linebreak = getLineBreak(data)
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

  def printMessage(self, name, text, linebreak="\n", replacer=""):  # replacer="↲"
    lineText = split(text, linebreak, replacer)
    previousLine = 0
    string = ""
    offsetString = ""
    for info in self.regex.matchLineInfo:
      # print(info)
      if info.line != previousLine:
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

  def printMessageOnly(self, name, linebreak="\n", replacer=""):  # replacer="↲"
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


def getLineBreak(string):
  crlfCount = string.count("\r\n")
  lfCount = string.count("\n")
  return "\r\n" if crlfCount != 0 and crlfCount == lfCount else "\n"


def split(string, separator="\n", replacer="\n"):  # replacer="↲"
  if string == "":
    return [string]
  work = string.split(separator)
  for i in range(len(work) - 1):
    work[i] += replacer
  # if work[len(work) - 1] == "":
  #   work.pop()
  return work


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
  parser.add_argument("-r", "--replace", nargs="?", const="", help="specify replace string. replace matching strings with this string.")  # 空文字列を受け取れる設定
  parser.add_argument("-rt", "--replaceTest", action="store_true",  help="Show only the result of replacement.")
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
