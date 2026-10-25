# Q54 fixture mutant (r22 defect shape)

This entry is a test artifact for `tests/fixtures/r23-locator-heading.py`'s selftest: its Gate
names a section that the cited snapshot does not have, which is exactly the round-22 defect
(`R22-M17`) Q54 exists to catch. The snapshot `census/round-22/attempt2/sources/man7-mv.1.txt`
has no OPTIONS heading.

- source: https://man7.org/linux/man-pages/man1/mv.1.html
- status: fixture-mutant, not a real entry

## Gate

### Opened sources

- ADMIT: "mv [OPTION]... SOURCE... DIRECTORY" — § OPTIONS --no-copy — reason: fixture mutant — snapshot: census/round-22/attempt2/sources/man7-mv.1.txt
