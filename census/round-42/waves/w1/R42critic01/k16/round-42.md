# Round 42 lesson: C1 declared-evidence calibration

The base SCORECARD.md carries 70 declared-evidence tokens that tools/souji-declared-evidence.py cannot resolve. census/round-42/c1-register.tsv accounts for each one. Five are unresolved and are corrected below, append-only.

CORRECTION-DE line=14 token=65817d0d derived=rev-unresolved rev=bf618f6c5c09d302994871c94903abbea2deb60d
CORRECTION-DE line=68 token=42259756a06538a5dfb81cb82fba20737eacdcfd5c06b9b36594071b26f9da44 derived=sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f rev=bf618f6c5c09d302994871c94903abbea2deb60d
CORRECTION-DE line=68 token=71b89eb3c7ce417979c5fce2c759dafe023af21d6310fde49197c766b8f28897 derived=sha256=bb506469be860f994f74f4c7d6eb1c949a4931b676cdb60f9f79de041d12f27f rev=bf618f6c5c09d302994871c94903abbea2deb60d
CORRECTION-DE line=92 token=09bb8e0d derived=rev-unresolved rev=bf618f6c5c09d302994871c94903abbea2deb60d
CORRECTION-DE line=175 token=c2-after.tsv derived=path-absent rev=bf618f6c5c09d302994871c94903abbea2deb60d

The row at line 14 is not a typo. `65817d0d` names revision history that the round-26 rebase rewrote out of the lane, so the rev-unresolved reading is the correct one.
