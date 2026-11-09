import subprocess, sys
def main():
    p = subprocess.run([sys.executable, "-B", "-c", "raise RuntimeError('child crash')"])
    print("child rc:", p.returncode)
    return 3
if __name__ == "__main__":
    sys.exit(main())
