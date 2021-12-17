import os
import argparse

import pyocr
import pyocr.builders
from PIL import Image

TesseractPath = r"C:\Program Files\Tesseract-OCR"


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
  tessarect = getTool()
  if tessarect is None:
    print("No OCR tool found")
    exit(1)
  return tessarect


def getPosition(box):
  return f"({box.position[0][0]}, {box.position[0][1]}, {box.position[1][0]}, {box.position[1][1]})"


def printPosition(lineBox):
  for l, line in enumerate(lineBox):
    print(f"{l}: {getPosition(line)}")
    for i, word in enumerate(line.word_boxes):
      print(f"  {i:>02}: [{word.content}], {word.confidence}, {getPosition(word)}")


def argumentParser():
  parser = argparse.ArgumentParser()
  parser.add_argument("path", help="path")
  parser.add_argument("-l", "--language", default="eng", help="language")
  parser.add_argument("-p", "--psm", type=int, default=3, help="page segment mode")
  parser.add_argument("-a", "--showArgument", action="store_true", help="show arguments.")
  return parser.parse_args()


if __name__ == "__main__":
  args = argumentParser()
  if args.showArgument:
    print(args)

  path = args.path
  language = args.language
  psm = args.psm

  tesseract = getTesseract()
  lineBox = tesseract.image_to_string(Image.open(path), lang=language, builder=pyocr.builders.LineBoxBuilder(tesseract_layout=psm))
  printPosition(lineBox)
