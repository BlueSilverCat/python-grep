import os.path
from pathlib import Path

from Sort import NaturalSorter

########################################################################################################################
## EntryInfo
########################################################################################################################

class EntryInfo():

  def __init__(self, path, depth=0, naturalSort=False):
    if not os.path.exists(path):
      print(path)
      raise ValueError
    self.path = os.path.abspath(path)
    self.name = os.path.basename(self.path) # 拡張子付き
    self.drive = os.path.splitdrive(self.path)[0]
    self.parent = os.path.split(self.path)[0] 
    # self.parent = EntryInfo(os.path.split(self.path)[0], naturalSort=naturalSort) # 無限にたどってしまうので無理
    self.prefix = os.path.splitext(self.name)[0] # 拡張子無し
    self.suffix = os.path.splitext(self.name)[1] # "."付き
    self.depth = depth
    self.naturalSort = naturalSort
    self.setAttribute()

  def __repr__(self):
    # return f"{'  ' * self.depth}{self.attribute}: {self.name}"
    return f"{self.attribute}: {self.name}"

  def __lt__(self, other):
    if self.attribute == other.attribute:
      if not self.naturalSort:
        return self.name > other.name
      return NaturalSorter.compare(other.name, self.name)
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
