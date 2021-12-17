import re

import utility

# NumberStringRegex = r"(?:-|\+)?\d+(?:\.\d+)?(?:[eE](?:-|\+)?\d+)?"
NumberStringRegex = r"\d+(?:\.\d+)?"

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

  def setInfoFromMatch(self, match, lastIndex=0):
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
## Regex
########################################################################################################################


class Regex:

  def __init__(self, pattern, flags=0): # flags = re.ASCII + re.IGNORECASE ...
    self.set(pattern, flags)

  def set(self, pattern, flags=0):
    self.pattern = pattern
    self.flags = flags
    self.regex = None
    self.includeZero = True
    # self.string = string
    self.matchInfo = []
    self.matchLineInfo = []
    self.compile()

  def __repr__(self):
    return f"pattern: {self.pattern}, flags: {self.flags}, matches: {len(self.matchInfo)}"

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
      self.matchInfo.append(MatchInfo().setInfoFromMatch(match, lastIndex))
    return Regex.getLastIndex(match, lastIndex)

  @staticmethod
  def getLastIndex(match, lastIndex=0):
    end = match.end() + lastIndex
    length = len(match[0])
    return end if length > 0 else end + 1

  # 文字列の中で一致しない箇所を格納する
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

  # 行番号を考慮した形式の情報を得る
  @staticmethod
  def getLineInfo(string, matchInfo, linebreak="\n"):
    lineInfo = []
    work = matchInfo.string
    matchLines = utility.split(work, linebreak)
    lineOffset = string.count(linebreak, 0, matchInfo.start)
    columnOffset = matchInfo.start - string[:matchInfo.start].rfind(linebreak) - 1
    for i in range(len(matchLines)):
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

  # 一致した箇所の情報を表示する。改行文字をただの文字として考える。
  def printInfo(self, invertMatch=False):
    for i in self.matchInfo:
      if i.invert == invertMatch:
        print(i)

  # 行番号を考慮して一致した箇所の情報を表示する。
  def printLineInfo(self, invertMatch=False):
    for i in self.matchLineInfo:
      if i.invert == invertMatch:
        print(i)

  # 文字列内でpatternが一致する箇所を調べる。
  def perform(self, string, linebreak="\n", includeZero=True, invertMatch=False):
    self.search(string, includeZero)
    if invertMatch:
      self.setInvert(string)
    self.setLineInfo(string, linebreak)
  
  # 指定したpatternで分割された文字列を返す。for natural sort.
  # setInvertとほとんど一緒の処理をしているので共通化出来ないか?
  def getSepareteText(self, string):
    self.search(string, False)

    start = 0
    result = []
    for match in self.matchInfo:
      if match.start > start:
        result.append(string[start:match.start])
      result.append(match.string)
      start = match.end
    if start < len(string):
      result.append(string[start:])
    return result
