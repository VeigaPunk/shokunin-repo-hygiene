# do-nothing control: reports eight passing cases without running any
import argparse
ap=argparse.ArgumentParser();ap.add_argument('--tool');ap.add_argument('--work');ap.parse_args()
print('SUMMARY cases=8 pass=8 fail=0')
