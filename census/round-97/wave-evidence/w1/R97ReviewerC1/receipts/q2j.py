import sys
class Big(Exception): pass
raise Big("x"*20000)
