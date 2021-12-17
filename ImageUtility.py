from PIL import Image, ImageFilter


def concat(image1, image2, vertical=False, coordinate1=(0, 0), coordinate2=(0, 0)):
  return concatVertical(image1, image2, coordinate1, coordinate2) if vertical else concatHorizontal(image1, image2, coordinate1, coordinate2)


def concatHorizontal(image1, image2, coordinate1=(0, 0), coordinate2=(0, 0)):
  height = image1.height if image1.height > image2.height else image2.height
  image = Image.new('RGB', (image1.width + image2.width, height))
  image.paste(image1, coordinate1)
  image.paste(image2, (image1.width + coordinate2[0], coordinate2[1]))
  return image


def concatVertical(image1, image2, coordinate1=(0, 0), coordinate2=(0, 0)):
  width = image1.width if image1.width > image2.width else image2.width
  image = Image.new('RGB', (width, image1.height + image2.height))
  image.paste(image1, coordinate1)
  image.paste(image2, (coordinate2[0], image1.height + coordinate2[1]))
  return image


# def clip(image, coordinate=(0, 0, 0, 0)):
#   return image.crop(coordinate)