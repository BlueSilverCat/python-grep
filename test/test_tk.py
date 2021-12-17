import sys
import os
import tkinter
from tkinter import scrolledtext

sys.path.append(os.path.abspath("."))


import logging
import loggerConfig

if __name__ == "__main__":
  logger = logging.getLogger(__name__)
  logger.info("start")

  Title = u"DarkestDungeon"
  Geometry = "600x400"

  root = tkinter.Tk()

  root.title(Title)
  root.geometry(Geometry)

  text_widget = scrolledtext.ScrolledText(root)
  text_widget.grid(column=0, row=0, sticky=(tkinter.N, tkinter.S, tkinter.E, tkinter.W))

  root.mainloop()