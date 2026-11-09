class Loud:
    def __del__(self):
        raise RuntimeError("del-boom")
obj = Loud()
