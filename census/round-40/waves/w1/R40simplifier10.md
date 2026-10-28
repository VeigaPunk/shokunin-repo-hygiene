# R40simplifier10 — C1 independent calibration attack

- Seat: simplifier (leaf; no dispatch)
- Scope: distinct item 10, **duplicate-anchor ambiguity / existential-hit acceptance**.
- Lane: `/home/vgpnk/Projects/shokunin/souji-shokunin`
- Frozen contract read first: `census/round-40/preregistration.txt`, C1 at line 5.
- Tool installs/upgrades: none; pacman untouched.

## Evidence and commands

Read-only source/receipt analysis; no candidate replay or synthetic fixture was run. Commands/tools actually used:

```text
read /home/vgpnk/.omp/agent/RULES.md
read skill://godspeed
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/preregistration.txt
bash: ls -la /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/ /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/ /home/vgpnk/Projects/shokunin/souji-shokunin/tools/ 2>/dev/null
bash: ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/ 2>/dev/null; ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/ 2>/dev/null; echo ---; ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/ 2>/dev/null
bash: ls /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/ 2>/dev/null; echo '--- items tsv:'; cat /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-40/c1-items.tsv
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-counter.py:107-259
read /home/vgpnk/Projects/shokunin/souji-shokunin/tools/souji-citation-reconcile.py:141-323
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/records/c1-before.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/records/c1-after.txt
read /home/vgpnk/Projects/shokunin/souji-shokunin/census/round-39/c1-items.tsv
read /home/vgpnk/Projects/shokunin/souji-shokunin/.ufo/waves/round-40/w1/R40scribe04.md
```

Observed evidence:

1. Frozen C1 requires each anchored item line to have a resolvable, revision-bound evidence pointer, and specifies the strict-descendant register condition (`census/round-40/preregistration.txt:5`).
2. The r39 item counter's item branch collects every line containing the anchor at `census/round-39/c1-counter.py:224-228`, then closes if **any** hit satisfies the token lists (`:229-240`). It neither requires `len(hits) == 1` nor checks revision-bound pointers for these item hits. By contrast, the same counter's register leg invokes the citation reconciler (`:155-184`); that reconciler rejects non-unique register anchors (`tools/souji-citation-reconcile.py:280-283`). This creates a specific asymmetry: register rows receive a uniqueness check while ordinary item rows are existential.
3. The r39 item table explains that line-unique anchors make its predicate re-derivable (`census/round-39/c1-items.tsv:4-5`), but the parser accepts arbitrary anchor values and does not enforce source-file hit uniqueness (`census/round-39/c1-counter.py:107-133,224-240`).
4. Concrete falsifier pattern for an implementation that preserves the r39 item branch: two lines in one item file contain the same anchor; one is a token-only forged line satisfying `must`, and the other is a different line. The `any`-hit branch can close the item without establishing that every anchored line is evidence-bound. This is a code-derived counterexample pattern, **not an observed r40 execution**.
5. The recorded r39 receipts show `c1-before.txt:3-20` all 16 items open / rc=1 and `c1-after.txt:3-21` all 16 closed, six register cells, zero register mismatches / rc=0. These are prior instrument outputs; neither exercises duplicate item anchors nor measures r40.
6. The r40 `c1-items.tsv` path does not exist yet (the attempted listing printed `cat: .../census/round-40/c1-items.tsv: No such file or directory`); round-40 census currently contains only its preregistration. No r40 counter bytes were available from that census directory during this inspection.

## Verdict

**Bounded falsifier target identified; r40 claim NOT MEASURED.** The distinct failure mode is duplicate-anchor ambiguity: an existential matching line may mask another token-only line sharing that anchor. The r39 implementation is demonstrably vulnerable by its branch structure, but this is not evidence that an r40 candidate retains the behavior. To resolve C1 on candidate bytes, construct a minimal item/file fixture with the same anchor on two lines (one pointerless token-satisfying forgery, one valid-looking citation), pin the audited revision and register revision, and require the item to remain OPEN or reject ambiguous anchors. Run the corresponding single-hit valid evidence control as well; verify it closes. Record exact candidate revision, both fixture bytes/hashes, full outputs/return codes, and scratch path. Keep this separate from the already-covered token-only single-line forgery and commit-vs-receipt_rev cases.

## Limits

- No candidate counter execution, mutation, git/jj/index operation, fixture, scratch, or verification check was performed.
- No production files or frozen claims changed; only this assigned report was written.
