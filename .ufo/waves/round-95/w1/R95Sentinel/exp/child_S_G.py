import concurrent.futures as cf, sys
if __name__ == "__main__":
    try:
        with cf.ProcessPoolExecutor(1) as ex:
            print("ppe:", ex.submit(lambda x: x * 2, 21).result())
    except Exception as exc:
        print("ppe-raised:", type(exc).__name__, exc)
        sys.exit(9)
