import re
import os

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


def getFileNumber(path):
  # (print(name) for name in os.listdir(path))
  return sum(os.path.isfile(os.path.join(path, name)) for name in os.listdir(path))


def getDirectoryNumber(path):
  return sum(os.path.isdir(os.path.join(path, name)) for name in os.listdir(path))


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


def getZeroFillNumberString(i, max, min=0):
  length = len(str(max))
  if length < min:
    length = min
  return str(i).zfill(length)


def makeDir(path):
  if not os.path.exists(path):
    os.makedirs(path)
  return os.path.abspath(path)


def checkFileName(path, makeDir=False):
  if makeDir:
    parrent = os.path.split(path)[1]
    makeDir(parrent)

  if not os.path.exists(path):
    return path
  root, ext = os.path.splitext(path)
  i = 1
  while True:
    suffix = getZeroFillNumberString(i, 0, 2)
    name = f"{root}_{suffix}{ext}"
    if not os.path.exists(name):
      return name
    i += 1
