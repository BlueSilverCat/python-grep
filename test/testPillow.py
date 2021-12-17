import sys
from PIL import Image

path = "orc_Bleed.png"

# im = Image.open(path)
# print(im.format, im.size, im.mode)  # PPM (512, 512) RGB
# im.show()

with Image.open(path) as im:
  print(path, im.format, f"{im.size}x{im.mode}")


