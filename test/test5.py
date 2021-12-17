import os, sys
from PIL import ImageGrab, Image

ImagePath = r"C:\Users\BlueSilverCat\Documents\Tesseract\DarkestDungeon.png"
DestinationPath = r"C:\Users\BlueSilverCat\Documents\Tesseract"

im = Image.open(ImagePath)
im_crop = im.crop((120, 52, 267, 80))
im_crop.save(os.path.join(DestinationPath, "clip.png"), quality=95)

