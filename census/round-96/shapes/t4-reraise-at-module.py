import sys
def helper():
    raise SystemExit("x")
saved = None
if __name__ == "__main__":
    try:
        helper()
    except SystemExit as e:
        saved = e
    try:
        raise saved
    except SystemExit:
        pass
