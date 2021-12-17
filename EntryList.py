import os
import os.path
from EntryInfo import EntryInfo

########################################################################################################################
## EntryList
########################################################################################################################


class EntryList:

  def __init__(self, path, reInclude=None, reExclude=None, naturalSort=False):
    self.entries = []
    self.getAllEntries(path, reInclude, reExclude, naturalSort)

  def getAllEntries(self, path, reInclude, reExclude, naturalSort):
    self.entries = [EntryInfo(path, naturalSort=naturalSort)]
    if self.entries[0].isFile():
      return

    workStack = []
    EntryList.getSubEntries(path, workStack, 1, naturalSort)
    while len(workStack) > 0:
      entry = workStack.pop()
      self.entries.append(entry)
      if entry.isDir():
        EntryList.getSubEntries(entry.path, workStack, entry.depth + 1, naturalSort)
    self.entries = EntryList.filterEntries(self.entries, reInclude, reExclude)

  @staticmethod
  def getSubEntries(path, stack, depth=0, naturalSort=False):
    lt = os.listdir(path)  # オブジェクトの型の問題で os.scandir(path) は使わないことにした
    entries = []
    for i in lt:
      entries.append(EntryInfo(os.path.join(path, i), depth, naturalSort))
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
