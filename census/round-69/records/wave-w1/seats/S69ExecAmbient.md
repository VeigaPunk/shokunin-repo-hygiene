souji round 69 — S69ExecAmbient (C2 falsification)

C2 frozen tuple: clean vs ambient (HOME .gitconfig showUntrackedFiles=no, XDG_CONFIG_HOME, GIT_TRACE=1, GIT_TRACE2_EVENT, GIT_TRACE2_PERF, env -i).

| variant | flips vs clean ^(CASE|SUMMARY|REGRESS|EXIT=) | EXIT | inside frozen tuple |
|---|---|---|---|
| clean candidate | — | 0 | yes (reference) |
| frozen ambient candidate | 0 | 0 | yes |
| wider (all: SSH/EXEC_PATH/TEMPLATE/ATTR_SOURCE/NO_LAZY_FETCH/CFG_SYSTEM/DISCOVERY/hostile HOME) | 100 | 1 | no |
| wider2 (minus EXEC_PATH) | 100 | 1 | no |
| wider3 minus ATTR_SOURCE minus TEMPLATE (SSH, CFG_SYSTEM, DISCOVERY, NO_LAZY_FETCH, hostile HOME/XDG fileMode=false) | 0 | 0 | no |
| do-nothing under frozen ambient | n/a (separate arm) EXIT=1, new_forgeries=3 | 1 | yes (its own control) |

Verdicts:
- Frozen ambient claim REPRODUCED: flips 0, EXIT 0, do-nothing EXIT 1 with new_forgeries=3 (controls/C2-do-nothing-ambient: EXIT=1 lines 6-8 match new_forgeries=3).
- Wider-tuple immunitya NOT held: two unscrubbed vars flip all verdicts (see below).

clean_env audit (census/round-69/c1-counter.py:319-339):
Scrubbed (excluded at 325-333): GIT_DIR, GIT_WORK_TREE, GIT_INDEX_FILE, GIT_OBJECT_DIRECTORY, GIT_ALTERNATE_OBJECT_DIRECTORIES, GIT_REPLACE_REF_BASE, GIT_CONFIG_COUNT, GIT_CONFIG_PARAMETERS, GIT_CONFIG_GLOBAL, GIT_CONFIG_NOSYSTEM, GIT_CONFIG_SYSTEM, GIT_NO_REPLACE_OBJECTS, GIT_COMMON_DIR, GIT_NAMESPACE, GIT_CEILING_DIRECTORIES, HOME, XDG_CONFIG_HOME, + GIT_CONFIG_KEY_*/GIT_CONFIG_VALUE_*/GIT_TRACE* prefixes. Re-pinned at 334-336: GIT_OPTIONAL_LOCKS=0, GIT_CONFIG_GLOBAL=os.devnull, GIT_CONFIG_NOSYSTEM=1. All counter git calls use it (git_run:342-344; hash-object/update-index:581-597; run_slot:751-752 env=clean_env(env_extra); git_show:832-833; run_fixture:866-868).
Not scrubbed: GIT_SSH, GIT_SSH_COMMAND, GIT_EXEC_PATH, GIT_TEMPLATE_DIR, GIT_ATTR_SOURCE, GIT_NO_LAZY_FETCH, GIT_DISCOVERY_ACROSS_FILESYSTEM, GIT_QUARANTINE_PATH, GIT_ALTERNATE_PATH(nonexistent as above?), GIT_CONFIG (legacy), GIT_PAGER, GIT_EXTERNAL_DIFF, GIT_ASKPASS, SSH_ASKPASS, GIT_TRACE? (scrubbed via prefix). The writer's own git() (tools/souji-receipt-write.py:97-106) only scrubs GIT_DIR/GIT_WORK_TREE/GIT_COMMON_DIR and pins GLOBAL/NOSYSTEM/NO_REPLACE_OBJECTS; likewise open to GIT_EXEC_PATH/GIT_TEMPLATE_DIR/GIT_ATTR_SOURCE/GIT_SSH for its own git calls.

Unscrubbed verdict-changers (measured):
- GIT_ATTR_SOURCE=HEAD — clean counter build fails: `fatal: bad --attr-source or GIT_ATTR_SOURCE`, `git add failed` on all 47 rows, errors=47, REGRESS FAIL, EXIT 1 (cand-wide.txt/cand-wide2.txt SUMMARY errors=47). Non-flip in limbo? Actually flip 100.
- GIT_EXEC_PATH=$S/hostile-exec (fake git binary) — total breakage in wide1 (part of the 100-flip pile). Mechanism: counter git_run and writer git() resolve git subprocess via GIT_EXEC_PATH; bogus dir removes real git plumbing. Isolated single-var check confirms any hostile GIT_EXEC_PATH replaces git behavior; wide1 combined EXIT1 errors=47.
- GIT_TEMPLATE_DIR=$S/hostile-tpl (hooks-only template) — crash in mutate(): FileNotFoundError .git/info/exclude, counter traceback at c1-counter.py:568 via evaluate:889 (cand-wide3.stderr). Template controls `git init` scaffolding; an unscrubbed template dir alters the fixture layout the counter then assumes.
- Not verdict-changing in this matrix: GIT_SSH=/bin/false, GIT_CONFIG_SYSTEM=$S/hostile-system-config (core.fileMode=false; scrubbed at line 329 + NOSYSTEM=1 re-pin), GIT_DISCOVERY_ACROSS_FILESYSTEM, GIT_NO_LAZY_FETCH=0, hostile HOME/XDG core.fileMode=false (HOME/XDG_CONFIG_HOME scrubbed). Wide3-minus (only those) flips 0, EXIT 0 (cand-wide3.txt). [clean_env does scrub GIT_CONFIG_SYSTEM, so the example in the task brief does NOT reach git — verified zero flips.]
- GIT_NO_LAZY_FETCH=0 alone has no observable effect on this offline, no-promisor git matrix (rc 0 on `git add`). Harmless here because no lazy-fetch path is exercised.

Findings:
- HIGH: C2's claim is tuple-scoped; outsiders reading "ambient immunity" get 100 flips / EXIT 1 from GIT_ATTR_SOURCE, GIT_EXEC_PATH, GIT_TEMPLATE_DIR — all adopted unscrubbed by the counter's fixture git calls and (exec/template) by the writer. The seal is only as wide as the tuple. The preregistration (preregistration.txt:82-89) is exact on this: "under the frozen ambient tuple".
- MEDIUM: Layer inconsistency — counter builds fixtures under an env that differs in open surface from the writer's allowed env (writer refuses GIT_DIR etc. but honours GIT_EXEC_PATH/template/attr source for its own git calls). A hostile outer env can starve writer git calls even as the counter's fixture builds survive.
- LOW: GIT_TEMPLATE_DIR's crash mode is an in-counter FileNotFoundError traceback at mutate:568, not a clean CASE error judgement. That path wants a judgement wrapper (cf. CaseError handling).

Commands run (cd /home/vgpnk/Projects/shokunin/souji-shokunin, fresh scratch under /fast/scratch/hyaku/souji-r69/S69ExecAmbient):
- python3 -B census/round-69/c1-counter.py --root $LANE --matrix census/round-69/c1-matrix.tsv --base-rev 3639087917eaeb28719d7603110a6ec22782100e --rev 893b8ef4e73b3fde45f712df3437a032b1d92d42 --tool tools/souji-receipt-write.py --work $S/work-clean --receipt $S/cand-clean.txt (EXIT 0)
- env -i PATH="$PATH" HOME=$S/amb-home XDG_CONFIG_HOME=$S/xdg GIT_TRACE=1 GIT_TRACE2_EVENT=$S/trace2-event.txt GIT_TRACE2_PERF=$S/trace2-perf.txt <same counter> --work $S/work-ambient --receipt $S/cand-ambient.txt (EXIT 0; flips 0)
- wider: env -i ... GIT_SSH GIT_EXEC_PATH GIT_TEMPLATE_DIR GIT_ATTR_SOURCE GIT_NO_LAZY_FETCH GIT_CONFIG_SYSTEM GIT_DISCOVERY_ACROSS_FILESYSTEM ... --work $S/work-wide --receipt $S/cand-wide.txt (EXIT 1, flips 100), plus wide2 (minus EXEC_PATH), wide3-minus (minus ATTR_SOURCE + TEMPLATE) table above; do-nothing: --new-tool $S/base-writer.py under frozen ambient (EXIT 1, new_forgeries=3)

Files written: .ufo/waves/round-69/w1/S69ExecAmbient.md (this file); scratch receipts only under $HYAKU_SCRATCH/souji-r69/S69ExecAmbient (cand-*.txt, noth-ambient.txt).
