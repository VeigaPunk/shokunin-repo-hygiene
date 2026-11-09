import subprocess, sys
p = subprocess.run([sys.executable, "-B", "-c", "raise SystemExit('child')"])
print("child rc:", p.returncode)
sys.exit(0)
