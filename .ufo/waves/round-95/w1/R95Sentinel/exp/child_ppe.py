import concurrent.futures as cf, os, sys, time
def work(x):
    return x * 2
if __name__ == "__main__":
    try:
        with cf.ProcessPoolExecutor(1) as ex:
            r = ex.submit(work, 21).result(timeout=30)
            print("ppe result:", r)
            time.sleep(1.5)
            print("ppe still alive")
    except Exception as exc:
        print("ppe-raised:", type(exc).__name__, exc)
        sys.exit(9)
