import re

from Regex import Regex, NumberStringRegex

########################################################################################################################
# NaturalSorter
########################################################################################################################


class NaturalSorter:
  NumberRegex = r"\d+"
  regex = Regex(NumberRegex)

  def __init__(self, string):
    self.data = string

  def __lt__(self, other):
    return NaturalSorter.compare(self.data, other.data)

  @classmethod
  def compare(cls, x, y):
    x = cls.regex.getSepareteText(x)
    y = cls.regex.getSepareteText(y)

    num = len(x)
    if len(x) > len(y):
      num = len(y)

    for i in range(num):
      if x[i] == y[i]:
        continue
      if re.match(cls.NumberRegex, x[i]) is not None and re.match(cls.NumberRegex, y[i]) is not None:
        return int(x[i]) < int(y[i])
      return x[i] < y[i]
    return len(x) < len(y)


def naturalSorted(args):
  work = sorted([NaturalSorter(s) for s in args])
  return [e.data for e in work]
