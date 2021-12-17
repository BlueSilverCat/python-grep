import json

config = {
  "config": [
    {
      "name": "Name",
      "coordinate": (1005, 775, 1180, 805),
      "operation": ["invert"],
    },
    {
      "name": "Type1",
      "coordinate": (1005, 825, 1090, 850),
      "operation": ["invert"],
    },
    {
      "name": "Type1Test",
      "coordinate": (1005, 820, 1090, 850),
      "operation": ["invert"],
    },
    {
      "name": "Type2",
      "coordinate": (1005, 845, 1090, 875),
      "operation": ["invert"],
    },
    {
      "name": "TypeTest",
      "coordinate": (1005, 820, 1090, 875),
      "operation": ["invert"],
    },
    {
      "name": "HP",
      "coordinate": (1505, 770, 1600, 805),
      "operation": ["invert"],
      "pattern": r"\d+/(?P<HP>\d+)"
    },
    {
      "name": "Block1",
      "coordinate": (1170, 825, 1290, 885),
      "operation": ["invert"],
      "pattern": r"(?:PROT: (?P<PROT>\d+%) )?DODGE: (?P<DODGE>\d+) SPD: (?P<SPD>\d+)"
    },  # DODGE, PROT, SPD
    {
      "name": "Stun",
      "coordinate": (1195, 940, 1255, 965),
      "operation": ["invert"],
    },
    {
      "name": "Blight",
      "coordinate": (1195, 960, 1255, 985),
      "operation": ["invert"],
    },
    {
      "name": "Bleed",
      "coordinate": (1195, 983, 1255, 1008),
      "operation": ["invert"],
    },
    {
      "name": "Debuff",
      "coordinate": (1195, 1005, 1255, 1030),
      "operation": ["invert"],
    },
    {
      "name": "Move",
      "coordinate": (1195, 1025, 1255, 1050),
      "operation": ["invert"],
    },
    {
      "name": "TestMove",
      "coordinate": (1060, 1025, 1255, 1050),
      "operation": ["invert"],
    },
  ],
  "printFormat":
    """\
{Name}
Type1={Type1}, Type2={Type2}
HP={HP}, PROT={PROT}, DODGE={DODGE}, SPD={SPD}
Stun={Stun}, Blight={Blight}, Bleed={Bleed}, Debuff={Debuff}, Move={Move}\
""",
  "outputFormat":
    "{Name}, {Type1}, {Type2}, {HP}, {PROT}, {DODGE}, {SPD}, {Stun}, {Blight}, {Bleed}, {Debuff}, {Move}\n"
}

with open("test.json", "w") as file:
  json.dump(config, file, indent=2)

with open("test.json", "r") as file:
  c = json.load(file)

print(c["outputFormat"].format(Name=1,Type1=2))