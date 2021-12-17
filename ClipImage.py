import os
import argparse
import re

from PIL import Image


def argumentParser():
  parser = argparse.ArgumentParser()
  parser.add_argument("inputPath", help="input path")
  parser.add_argument("outputPath", help="output path")
  parser.add_argument("coordinate", help="coordinate (leftX, leftY, rightX, rightY)")
  return parser.parse_args()


def getCoordinate(string):
  match = re.search(r"\((\d+), *(\d+), *(\d+), *(\d+),?\)", string)
  return [int(match) for match  in match.groups()]


if __name__ == "__main__":
  args = argumentParser()

  inputPath = args.inputPath
  outputPath = args.outputPath
  coordinate = args.coordinate

  image = Image.open(inputPath)
  coordinate = getCoordinate(coordinate)
  image = image.crop(coordinate)
  image.save(outputPath)
