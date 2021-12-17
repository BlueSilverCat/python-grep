def replaceRange(string, ranges, repl):
  work = string
  length = len(work)
  for range in ranges:
    diff = len(work) - length
    work = work[:range[0]+diff] + repl + work[range[1]+diff:]
  return work

string = "01234567890"

r = replaceRange(string, [(1,3), (4,6), (7,8), (9,10)], "")
print(r)
