import os
import re
import argparse
from collections import defaultdict

import pyocr
import pyocr.builders
from PIL import Image, ImageDraw, ImageOps

from CheckOcr import printPosition

TesseractPath = r"C:\Program Files\Tesseract-OCR"

Config = [
  {
    "name": "Name",
    "coordinate": (1005, 775, 1180, 805),
    "operation": ["invert"],
  },
  {
    "name": "Type1",
    "coordinate": (1005, 825, 1090, 850),
    "operation": ["invert"],
  },
  # {
  #   "name": "Type1Test",
  #   "coordinate": (1005, 820, 1090, 850),
  #   "operation": ["invert"],
  # },
  {
    "name": "Type2",
    "coordinate": (1005, 845, 1090, 875),
    "operation": ["invert"],
  },
  # {
  #   "name": "TypeTest",
  #   "coordinate": (1005, 820, 1090, 875),
  #   "operation": ["invert"],
  # },
  {
    "name": "HP",
    "coordinate": (1505, 770, 1600, 805),
    "operation": ["invert"],
    "pattern": r"\d+/(?P<HP>\d+)"
  },
  {
    "name": "Block1",
    "coordinate": (1170, 825, 1290, 895),
    "operation": ["invert"],
    "pattern": r"(?:PROT: (?P<PROT>\d+%) )?DODGE: (?P<DODGE>\d+) SPD: (?P<SPD>\d+)"
  },  # DODGE, PROT, SPD
  {
    "name": "Stun",
    "coordinate": (1195, 940, 1255, 965),
    "operation": ["invert"],
  },
  {
    "name": "Blight",
    "coordinate": (1195, 960, 1255, 985),
    "operation": ["invert"],
  },
  {
    "name": "Bleed",
    "coordinate": (1195, 983, 1255, 1008),
    "operation": ["invert"],
  },
  {
    "name": "Debuff",
    "coordinate": (1195, 1005, 1255, 1030),
    "operation": ["invert"],
  },
  {
    "name": "Move",
    "coordinate": (1195, 1025, 1255, 1050),
    "operation": ["invert"],
  },
  # {
  #   "name": "TestMove",
  #   "coordinate": (1060, 1025, 1255, 1050),
  #   "operation": ["invert"],
  # },
]

PrintFormat = """\
================================================================================
{Name}
Type: {Type1}, {Type2}
HP={HP}, PROT={PROT}, DODGE={DODGE}, SPD={SPD}
Stun={Stun}, Blight={Blight}, Bleed={Bleed}, Debuff={Debuff}, Move={Move}\
"""

OutputFormat = "{Name}, {Type1}, {Type2}, {HP}, {PROT}, {DODGE}, {SPD}, {Stun}, {Blight}, {Bleed}, {Debuff}, {Move}\n"


def setPath(path):
  if path not in os.environ["PATH"].split(os.pathsep):
    os.environ["PATH"] += os.pathsep + path


def getTool(name="Tesseract (sh)"):
  tools = pyocr.get_available_tools()
  if len(tools) == 0:
    return None
  for tool in tools:
    if tool.get_name() == name:
      return tool
  return None


def getTesseract():
  setPath(TesseractPath)
  tesseract = getTool()
  if tesseract is None:
    print("No OCR tool found")
    exit(1)
  return tesseract


# Keyが存在しない場合、""を返すDict
# collections の defaultdict を 使っても良い
class FormatDict(dict):

  def __missing__(self, key):
    return ""


class OCR():

  def __init__(self, args, config, outputFromat=None, printFormat=None):
    self.inputPath = args.inputPath
    self.outputPath = args.outputPath
    self.language = args.language
    self.psm = args.psm
    self.clippedImage = args.clippedImage
    self.showConfidence = args.showConfidence
    # utility.makeDir(self.outputPath)
    self.tesseract = getTesseract()
    self.image = Image.open(self.inputPath)
    self.config = config
    self.result = FormatDict({})
    self.printFormat = printFormat
    self.outputFormat = outputFromat

  def perform(self):
    self.read()
    self.print()
    self.save()

  def read(self):
    for data in self.config:
      image = self.getImage(data)
      self.saveClippedImage(image, data)
      self.getText(image, data)
    return

  def print(self):
    if self.printFormat is None:
      return
    print(self.printFormat.format_map(self.result))

  def save(self, linebreak=True):
    if self.outputFormat is None:
      return
    text = self.outputFormat.format_map(self.result)
    if linebreak and text[len(text) - 1] != "\n":
      text += "\n"
    with open(self.outputPath, "a", encoding="utf-8") as file:
      file.write(text)

  def getImage(self, data):
    image = self.image.crop(data["coordinate"])
    image = self.invert(image, data)
    #self.border(image, data)
    return image

  def saveClippedImage(self, image, data):
    if self.clippedImage:
      image.save(f"orc_{data['name']}.png", quality=100)

  def getText(self, image, data):
    text, confidence = self.recognition(image)
    self.printConfidence(data["name"], text, confidence)
    if data.get("pattern"):
      matches = re.search(data.get("pattern"), text)
      if matches is not None:
        for name, text in matches.groupdict("").items():
          self.result[name] = text
        return
    self.result[data["name"]] = text

  def recognition(self, image):
    # text = self.tesseract.image_to_string(image, lang=self.language, builder=pyocr.builders.TextBuilder(tesseract_layout=self.psm))
    box = self.tesseract.image_to_string(image, lang=self.language, builder=pyocr.builders.WordBoxBuilder(tesseract_layout=self.psm))
    text = ""
    confidence = []
    for data in box:
      text += data.content + " "
      confidence.append(data.confidence)
    text = text.rstrip()
    return text, confidence

  def printConfidence(self, name, text, confidence):
    if self.showConfidence:
      print(f"{name}: \"{text}\" {confidence}")

  @staticmethod
  def trimmingText(text):
    text = re.sub("\n", " ", text)
    return re.sub(" +", " ", text)

  @staticmethod
  def invert(image, data):
    if "invert" in data.get("operation"):
      # image = image.convert("L")
      image = ImageOps.invert(image)
    return image

  @staticmethod
  def border(image, data):
    draw = ImageDraw.Draw(image)
    draw.rectangle((0, 0, data["coordinate"][2] - data["coordinate"][0] - 1, data["coordinate"][3] - data["coordinate"][1] - 1), outline=(255, 255, 255))


def argumentParser():
  parser = argparse.ArgumentParser()
  parser.add_argument("inputPath", help="input path")
  parser.add_argument("outputPath", help="output path")
  parser.add_argument("-l", "--language", default="eng", help="language")
  parser.add_argument("-p", "--psm", type=int, default=3, help="page segment mode")
  parser.add_argument("-c", "--clippedImage", action="store_true", help="output clippedImage")
  parser.add_argument("-s", "--showConfidence", action="store_true", help="show confidence")
  parser.add_argument("-a", "--showArgument", action="store_true", help="show arguments.")
  return parser.parse_args()


if __name__ == "__main__":
  args = argumentParser()
  if args.showArgument:
    print(args)

  ocr = OCR(args, Config, OutputFormat, PrintFormat)
  ocr.perform()