```
re.sub("\d*", "X", "abc123def456")
'XaXbXcXXdXeXfXX'
```

---

```
>>>re.sub(".\*", "X", "abc\n123\n")
'XX\nXX\nX'

>>> re.sub(".\*", "X", "abc\r\n123\r\n")
'XX\nXX\nX'

>>> re.sub(".*", "X", "abc\n")
'XX\nX'
>>> re.sub(".*", "X", "123\n")
'XX\nX'

>>> re.sub(".*", "X", "abc")
'XX'
>>> re.sub(".*", "X", "123")
'XX'
```

---

# vscode

```
abc
123

```

```
X
X
X
```

"\d\*", "X"

```
1:
2:
3:
4:
5:
```

```
XX:X
XX:X
XX:X
XX:X
XX:X
```

"+\*", "X"

```
X
X
X
X
X
```

---

"abc".replace(/.\*/, "X")
"X"

---

```
1:
2:
3:
4:
5:
```

grep.py "\d\*"
改行削除無し

```
XX:X
XXX:X
XXX:X
XXX:X
XXX:X
```

grep.py "\d\*"
改行削除あり

```
XX:X
XX:X
XX:X
XX:X
XX:X
```

grep.py ".\*"
改行削除なし

```
XX
XXX
XXX
XXX
XXX
```

grep.py ".\*"
改行削除あり

```
XX
XX
XX
XX
XX
```
