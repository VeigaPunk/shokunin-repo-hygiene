import multiprocessing, sys
def w(x):
    return x * 2
if __name__ == "__main__":
    try:
        with multiprocessing.Pool(1) as p:
            print("map:", p.map(w, [21]))
    except Exception as exc:
        print("pool-raised:", type(exc).__name__, exc)
        sys.exit(9)
    print("pool-ok")
