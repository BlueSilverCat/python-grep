import re

path1 = r"C:\Users\blues\onedrive\github\python-grep\test\test6.txt"


class MatchLineInfo:

  def __init__(self, line, start, end, length, string, invert):
    self.line = line
    self.start = start
    self.end = end
    self.length = length
    self.string = string
    self.invert = invert

  def __repr__(self):
    return f"{self.line}: [{self.start}--{self.end}]({self.length})\"{self.string}\" {self.invert}"


class MatchInfo:

  def __init__(self):
    self.start = -1
    self.end = -1
    self.length = -1
    self.string = None
    self.invert = False
    self.lineInfo = []

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

  def setLineInfo(self, string, linebreak="\n"):
    # work = self.string.rstrip(linebreak)
    work = self.string
    # matchLines = work.split(linebreak)
    matchLines = split(work, linebreak)
    # matchLines = self.string.split(linebreak)
    lineOffset = string.count(linebreak, 0, self.start)
    columnOffset = self.start - string[:self.start].rfind(linebreak) - 1
    self.lineInfo = []
    for i in range(len(matchLines)):
      lineNumber = lineOffset + i
      self.lineInfo.append(
          MatchLineInfo(line=lineOffset + i, start=columnOffset, end=columnOffset + len(matchLines[i]),
                        length=len(matchLines[i]), string=matchLines[i], invert=self.invert))
      columnOffset = 0


def split(string, separator="\n", replacer="↲"):
  if string == "":
    return [string]
  work = string.split(separator)
  for i in range(len(work) - 1):
    work[i] += replacer
  if work[len(work) - 1] == "":
    work.pop()
  return work


class Regex:

  def __init__(self, pattern, flags=0):
    self.pattern = pattern
    self.flags = flags
    self.regex = None
    self.includeZero = True
    # self.string = string
    self.matchInfo = []
    self.compile()

  def __repr__(self):
    return f"{self.pattern}, {self.flags}, {len(self.matchInfo)}"

  def compile(self):
    self.regex = re.compile(self.pattern, self.flags)

  def search(self, text, includeZero=True):
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
        work.append(MatchInfo().setInfo(start, i.start, string[start: i.start], True))
      start = i.end
    if start < len(string):
      work.append(MatchInfo().setInfo(start, len(string), string[start:], True))
    self.matchInfo += work
    self.matchInfo.sort()
  
  def setLineInfo(self, string):
    for i in self.matchInfo:
      i.setLineInfo(data)

  def printInfo(self):
    for i in self.matchInfo:
      print(i)

  def printLineInfo(self):
    for i in self.matchInfo:
      for l in i.lineInfo:
        print(i)

def f(path):
  with open(path, "r", encoding="utf-8", newline="") as file:
    data = file.read()
  # print(data, len(data))
  return data


# def countLineBeak(string, regex=None):
#   if regex is None:
#     regex =re.compile("\n")
#   return len(regex.findall(string))


# def GetInvert(matchList, string, linebreak="\n"):
#   lines = string.split(linebreak)
#   matchedLines = ff(matchList)
#   for i in range(len(lines)):
#     if i not in matchedLines:
#       matchList.append({
#           "line": i,
#           "start": 0,
#           "end": len(lines[i]),
#           "length": len(lines[i]),
#           "string": lines[i],
#           "invert": True
#       })
#   matchList.sort(key=lambda x: str(x["line"]) + str(x["start"]))


def ff(lt):
  result = []
  for v in lt:
    result.append(v["line"])
  return result


# class RegexInfo:
#   def __init__(self):
#     pass
#   def __lt__():

data = f(path1)
print(data)

regex = Regex("\d+")
regex.search(data)
print(regex)
regex.setInvert(data)
regex.setLineInfo(data)
regex.printInfo()
regex.printLineInfo()


# r = data.count("\n")
# print(r)
# # r = re.findall("\n", data)
# # print(r, len(r))

# lt2 = []
# for v in lt:
#   getLineNumber(v, data, lt2)
# print(lt2)

# GetInvert(lt2, data)
# print(lt2)

# def printInfo(lt):
#   beforeLine = 0
#   beforeEnd = 0
#   string = ""
#   for v in lt:
#     if v["line"] == beforeLine:
#       if (v["start"] == beforeEnd):
#         string += v["string"]
#       else:
#         string = v["string"]
#     else:
#       print(f"#{string}")
#       string = v["string"]
#     beforeLine = v["line"]
#     beforeEnd = v["end"]


def printInfo(lt, text, linebreak="\n"):
  beforeLine = -1
  lines = text.split(linebreak)
  for v in lt:
    if v["line"] != beforeLine:
      print(lines[v["line"]])
    beforeLine = v["line"]


# printInfo(lt2, data)
