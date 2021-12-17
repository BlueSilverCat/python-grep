import sys
import os

sys.path.append(os.path.abspath("."))

import utility

import pyocr
import pyocr.builders
from PIL import Image

def setTesseractPath():
  TesseractPath = "C:\\Program Files\\Tesseract-OCR"
  if TesseractPath not in os.environ["PATH"].split(os.pathsep):
      os.environ["PATH"] += os.pathsep + TesseractPath

def getTesseract():
  tools = pyocr.get_available_tools()
  if len(tools) == 0:
    # print("No OCR tool found")
    return None
  for tool in tools:
    if tool.get_name() == "Tesseract (sh)":
      print("Will use tool '%s'" % (tool.get_name()))
      return tool
  return None

ImagePath = r"C:\Users\BlueSilverCat\Documents\Tesseract\DarkestDungeon.png"

setTesseractPath()
tessarect = getTesseract()

txt = tessarect.image_to_string(
    Image.open(ImagePath),
    lang="eng",
    builder=pyocr.builders.TextBuilder()
)
print(txt)

word_boxes = tessarect.image_to_string(
    Image.open(ImagePath),
    lang="eng",
    builder=pyocr.builders.WordBoxBuilder()
)
for i in word_boxes:
  print(i)

line_and_word_boxes = tessarect.image_to_string(
    Image.open(ImagePath), lang="eng",
    builder=pyocr.builders.LineBoxBuilder()
)

for i in line_and_word_boxes:
  print(i)

digits = tessarect.image_to_string(
    Image.open(ImagePath),
    lang="eng",
    builder=pyocr.tesseract.DigitBuilder()
)
print(digits)