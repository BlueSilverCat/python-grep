import sys
import os

sys.path.append(os.path.abspath("."))

import Sort

data = ["abc1", "abc2", "abc10", "abc20"]
data.sort()
print(data)

st = Sort.naturalSorted(data)
print(st)