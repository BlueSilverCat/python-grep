import pickle

d = { 'Apple': 4, 'Banana': 2, 'Orange': 6, 'Grapes': 11}

with open("a.txt", "wb") as file:
  pickle.dump(d, file)
