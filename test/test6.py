class format_dict(dict):

  def __missing__(self, key):
    return "..."


d = format_dict({})

d["foo"] = "name"

print("My %(foo)s is %(bar)s" % d)  # "My name is ..."

print("My {foo} is {bar}".format_map(d))  # "My name is ..."


# class Default(dict):

#   def __missing__(self, key):
#     print(f"{self}, {key}, {dir(key)}")
#     return key.join("{}")


# d = Default({"foo": "name"})

# print(d["cat"])