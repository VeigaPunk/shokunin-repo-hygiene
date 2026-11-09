import subprocess, sys
def main():
    p = subprocess.run([sys.executable, "-B", "-c", "raise SystemExit(9)"])
    print("child rc:", p.returncode)
    return 3
if __name__ == "__main__":
    sys.exit(main())
