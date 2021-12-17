import argparse
import os
import re

import fitz
# from PIL import Image, ImageFilter

from EntryList import EntryList
import utility

########################################################################################################################
## ImageFromPDF
## PDFを画像にする
########################################################################################################################


class ImageFromPDF:

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

  def __repr__(self):
    return f"{self.path}, {self.prefix}, {self.suffix}, {len(self.files)}"

  def perform(self):
    for entry in (self.entries):
      if not entry.isFile() or entry.suffix != ".pdf":
        continue
      print(entry.name)
      with fitz.open(entry.path) as pdf:
        pixmaps = self.readPixmap(pdf)
        self.savePixmap(entry.prefix, pixmaps)

  def readPixmap(self, pdf):
    pixmaps = []
    for page in pdf:
      # images.append(page.getImageList())
      pixmaps.append(page.get_pixmap())
    return pixmaps

  def savePixmap(self, fileName, pixmaps):
    for page, data in enumerate(pixmaps):
      name = self.createName(fileName, page, len(pixmaps))
      # print(f"{name}") # 出力ファイル名の出力
      data.save(name)

  def createName(self, title, currentPage, maxPage, extension=".png"):
    page = utility.getZeroFillNumberString(currentPage, maxPage)
    title = re.sub(" ", "", title)
    # return os.path.join(self.destination, f"{self.prefix}{title}_{page}{self.suffix}{extension}")
    name = os.path.join(self.destination, title, f"{self.prefix}{page}{self.suffix}{extension}")
    utility.makeDir(os.path.split(name)[0])
    return name

def argumentParser():
  parser = argparse.ArgumentParser()
  parser.add_argument("path", help="ディレクトリのパスを指定する")

  parser.add_argument("-d", "--destination", default="", help="保存先のパス")
  parser.add_argument("-p", "--prefix", default="", help="共通の接頭辞を指定する")
  parser.add_argument("-s", "--suffix", default="", help="共通の接尾辞を指定する")

  parser.add_argument("-a", "--showArgument", action="store_true", help="show arguments.")

  return parser.parse_args()


if __name__ == "__main__":
  args = argumentParser()
  if args.showArgument:
    print(args)

  ic = ImageFromPDF(args)
  ic.perform()