import argparse
import os
from PIL import Image, ImageFilter

from EntryList import EntryList
import utility
import ImageUtility

########################################################################################################################
## ImageConcat
## 画像を結合する
########################################################################################################################


class ImageConcat:

  def __init__(self, args):
    self.setSearchOption(args)
    self.entries = EntryList(self.path, naturalSort=True).entries
    self.setDestination(self.entries[0], args.destination)

  def setDestination(self, entry, dest):
    self.destination = self.path
    if dest != "":
      self.destination = utility.makeDir(dest)

  def setSearchOption(self, args):
    self.path = args.path
    self.prefix = args.prefix
    self.suffix = args.suffix
    self.bidi = args.bidi
    self.rotate = args.rotate
    self.vertical = args.vertical

  def __repr__(self):
    return f"{self.path}, {self.prefix}, {self.suffix}, {self.bidi}, {self.rotate}, {len(self.entries)}"

  def perform(self):
    directories = self.getChildren()
    for files in directories:
      print(os.path.basename(files[0].parent))
      self.num = len(files)
      i = 0
      self.createCount = 0
      while i < self.num:
        if self.checkConcat(files, i) == 2 and self.checkConcat(files, i + 1) == 2:
          self.concat(files[i], files[i + 1])
          i += 2
        elif self.checkConcat(files, i) == 3 and self.checkConcat(files, i + 1) == 3 and self.checkConcat(files, i + 2) == 3:
          self.concat3(files[i], files[i + 1], files[i + 2])
          i += 3
        else:
          self.save(files[i])
          i += 1

  def checkConcat(self, entries, i):
    if i >= self.num:
      return 1
    if entries[i].prefix[len(entries[i].prefix) - 1] == "_":
      return 1
    if entries[i].prefix[len(entries[i].prefix) - 1] == "!":
      return 3
    return 2

  def save(self, entry):
    with Image.open(entry.path) as image:
      name = self.createName(entry)
      image = self.rotateImage(image)
      image.save(name)

  def concat(self, x, y):
    with Image.open(x.path) as image1, Image.open(y.path) as image2:
      image1, image2 = self.swap(image1, image2)
      name = self.createName(x)
      image = ImageUtility.concat(image1, image2, vertical=self.vertical)
      image = self.rotateImage(image)
      # print(name)
      image.save(name)

  def concat3(self, x, y, z):
    with Image.open(x.path) as image1, Image.open(y.path) as image2, Image.open(z.path) as image3:
      image1, image3 = self.swap(image1, image3)
      name = self.createName(x)
      image = ImageUtility.concat(image1, image2, vertical=self.vertical)
      image = ImageUtility.concat(image, image3, vertical=self.vertical)
      image = self.rotateImage(image)
      # print(name)
      image.save(name)

  def getChildren(self):
    directories = []
    work = []
    parentOld = ""
    for entry in self.entries:
      if not entry.isFile() or (entry.suffix.lower() != ".png" and entry.suffix.lower() != ".jpg"):
        continue
      if parentOld != "" and entry.parent != parentOld:
        directories.append(work)
        work = []
      parentOld = entry.parent
      work.append(entry)
    directories.append(work)
    return directories

  def swap(self, path1, path2):
    if self.bidi:
      return path2, path1
    return path1, path2

  def createName(self, entry):
    number = utility.getZeroFillNumberString(self.createCount, self.num)
    name = os.path.join(self.destination, os.path.basename(entry.parent), f"{self.prefix}{os.path.basename(entry.parent)}_{number}{self.suffix}{entry.suffix}")
    utility.makeDir(os.path.split(name)[0])
    self.createCount += 1
    return name

  def rotateImage(self, image):
    return image.rotate(self.rotate, expand=True)


def argumentParser():
  parser = argparse.ArgumentParser()
  parser.add_argument("path", help="ディレクトリのパスを指定する")

  parser.add_argument("-d", "--destination", default="", help="保存先のパス")
  parser.add_argument("-p", "--prefix", default="", help="共通の接頭辞を指定する")
  parser.add_argument("-s", "--suffix", default="", help="共通の接尾辞を指定する")

  parser.add_argument("-b", "--bidi", action="store_true", help="1枚目を右に置く")
  parser.add_argument("-r", "--rotate", type=int, default=0, help="回転角度")
  parser.add_argument("-v", "--vertical", action="store_true", help="縦に連結する")

  parser.add_argument("-a", "--showArgument", action="store_true", help="show arguments.")

  return parser.parse_args()


if __name__ == "__main__":
  args = argumentParser()
  if args.showArgument:
    print(args)

  ic = ImageConcat(args)
  ic.perform()