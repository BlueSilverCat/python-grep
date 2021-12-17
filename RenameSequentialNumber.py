from Sort import naturalSorted
import argparse
import os.path

from EntryList import EntryList
from Regex import Regex, NumberStringRegex
import utility

########################################################################################################################
## RenameSequentialNumber
## ファイル名を連番の数字に置き換える
########################################################################################################################


class RenameSequentialNumber:

  def __init__(self, args):
    self.setSearchOption(args)
    self.entryList = EntryList(self.path, naturalSort=True)

  def setSearchOption(self, args):
    self.path = args.path
    self.prefix = args.prefix
    self.suffix = args.suffix
    self.whatIf = args.whatIf

  def __repr__(self):
    return f"{self.path}, {self.prefix}, {self.suffix}, {len(self.entryList.entries)}"

  def perform(self):
    total = len(self.entryList.entries) - 1  # ディレクトリも含まれているので -1 する
    i = 0
    for entryInfo in self.entryList.entries:
      if not entryInfo.isFile():
        continue
      newPath = self.rename(entryInfo, i, total)
      self.print(entryInfo.path, newPath)
      i += 1

  def rename(self, entryInfo, i, max):
    number = utility.getZeroFillNumberString(i, max)
    newPath = os.path.join(entryInfo.parent, f"{self.prefix}{number}{self.suffix}{entryInfo.suffix}")
    if not self.whatIf:
      os.rename(entryInfo.path, newPath)
    return newPath

  def print(self, oldPath, newPath):
    oldName = os.path.basename(oldPath)
    newName = os.path.basename(newPath)
    print(f"{oldName} -> {newName}")


########################################################################################################################
## argument
########################################################################################################################


def argumentParser():
  parser = argparse.ArgumentParser()
  parser.add_argument("path", help="名前を変更したいファイルが入っているディレクトリのパスを指定する")
  parser.add_argument("-p", "--prefix", default="", help="共通の接頭辞を指定する")
  parser.add_argument("-s", "--suffix", default="", help="共通の接尾辞を指定する")
  parser.add_argument("-w", "--whatIf", action="store_true", help="only show log")
  parser.add_argument("-a", "--showArgument", action="store_true", help="show arguments.")
  return parser.parse_args()


########################################################################################################################
## main
########################################################################################################################

if __name__ == "__main__":
  args = argumentParser()
  if args.showArgument:
    print(args)

  rsn = RenameSequentialNumber(args)
  rsn.perform()