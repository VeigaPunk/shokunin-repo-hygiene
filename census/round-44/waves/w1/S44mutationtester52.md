# S44mutationtester52

Result: **KILLED** — duplicate-key occurrence deduplication mutant failed hidden-audit h6 normally, not by crashing.

Pristine: exit 0, `SUMMARY scenarios=10 pass=10 fail=0`.
Mutated: exit 1, `SUMMARY scenarios=10 pass=9 fail=1`.
Restored: exit 0, `SUMMARY scenarios=10 pass=10 fail=0`.

Full scoped report, exact commands, hashes, outputs and limitations: [S44mutationtester52/report.md](S44mutationtester52/report.md).

Exact original scratch tool bytes restored; seat scratch deleted. Frozen counter/audit unchanged. Full C2 counter not executed; only bounded audit and counter verdict parser exercised. No admission/closure or numerical score claim.
