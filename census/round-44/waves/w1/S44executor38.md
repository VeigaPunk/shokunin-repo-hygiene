Probe command: python3 -B tests/fixtures/r38-drift-write-envelope.py --tool <freeze tools/souji-worktree-drift.py> --base-tool base-tool.py --work work
Observed: fixture exit 0; 12/12 freeze fixture cases PASS. The explicitly requested base arm reports one expected r44 cutover difference, json-symlink-refused, with rc=0 and resolved_written=True.
Probe command: python3 -B tests/fixtures/r38-drift-write-envelope.py --tool base-tool.py --work work
Observed: base 55d7af6 behavior is 11/12; json-symlink-refused writes through the leaf symlink; this is the intended baseline negative, not a frozen-candidate failure.

Tool hashes: base 55d7af6 tools/souji-worktree-drift.py b2a603cf42472b458712f2997fe6635c92147b75f5352c005cb7916ab3e34dc6; freeze d314fd6 tools/souji-worktree-drift.py 4d6bb64312e1cb52863d4d3b95f32503b6ff8d8189680d940b280ffcd21c490d.

Findings: frozen candidate passes the r38 output-envelope behavior including regular output success and refusals for FIFO output with/without reader, record alias and hardlink alias without changing record bytes, output inside measured tree, hardlinked output, leaf symlink, directory output, and outside-root record. The base arm reproduces the leaf-symlink output-write defect; cutover affects this case and prevents that write.

Limitations: bounded legacy fixture exercised; does not establish behavior beyond its 12 cases or certify admission. First setup invocation lacked existing --work directory and exited 2 without probing; rerun used created isolated work directory. No tools installed. No production/sibling/shared files changed.
