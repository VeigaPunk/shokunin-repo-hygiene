# Freeze-record substance binding — what a red control receipt must name

ground: F1 — git-native housekeeping vs receipts (the binding a frozen claim's control receipt
needs before its red exit can be read as evidence, and the limit of that binding)
source: S288 — Python `os.replace` atomicity (opened r60); S251 — `git merge-base --is-ancestor`
exit-status contract (re-opened r60); S284 — `git cat-file -t` object type (r58)
verified-at: 2026-11-04 — S288 and S251 re-fetched this round; located quotes and access records in
`corpus/lessons/round-60.md` `## Gate`
recheck: 90d — the pages are versioned manuals (Python 3.15.2 docs; git web manual 2.56.0)

# A label-only freeze grammar cannot see a vacuous control

## Claim (F1, sourced)

QUALITY Q99 freezes a claim when its preregistration carries `Base:`, `Counter:`, `Population:`,
`Control:`, `Target:` and `Kill:`, and when the `Control:` receipt's blob at the freeze commit ends
in `EXIT=<nonzero>`. That grammar binds **labels**. It does not bind the receipt to the instrument
the claim says it ran, nor to a revision that existed before the freeze. Five states therefore pass
the grammar while carrying no evidence:

| forgery class | what the receipt carries | why the label grammar accepts it | finding the substance arm raises |
|---|---|---|---|
| kind-only | `EXIT=1` and nothing else | the last line is the only thing read | `CONTROL-INSTRUMENT-MISSING` |
| digest-forged | `instrument_sha256=` of some other blob | no digest comparison exists | `CONTROL-INSTRUMENT-MISMATCH` |
| rev-at-freeze | `rev=` equal to the freeze commit | no ancestry is evaluated | `CONTROL-REV-NOT-BEFORE-FREEZE` |
| rev-missing | no `rev=` line | nothing requires one | `CONTROL-REV-MISSING` |
| command-other | `command=` naming a different tool | no cross-check against `Counter:` | `CONTROL-COMMAND-MISMATCH` |

The substance arm closes the label gap with four bindings, each read from the object store at the
freeze commit: the receipt must name the declared `Counter:` path (`instrument=`), that path's blob
digest at the freeze commit (`instrument_sha256=`), a full-40 revision that `git merge-base
--is-ancestor` reports as a **strict** ancestor of the freeze commit (`rev=`), and a `command=`
line containing the declared counter path.

## What the binding still cannot prove

- **Bytes, not execution.** A receipt that truthfully reports the right digest and the right revision
  still only proves those two facts. Nothing here proves the command ran, or that the command it
  names is the program that ran. `git cat-file -t` (S284) distinguishes a commit from a raw tag OID;
  it does not authenticate a run.
- **A truthful forgery passes.** An author who fabricates a receipt with a real ancestor revision and
  the real counter digest is accepted. The arm raises the cost of a vacuous control; it is not an
  authenticity proof, and it never becomes one inside this lane.
- **Ancestry is not chronology of the run.** `--is-ancestor` (S251) reports a graph relation between
  two commits: it says the receipt's `rev=` predates the freeze *in history*, not that the control was
  executed before the freeze in wall-clock time. A commit made early and measured late satisfies it.
- **Rename atomicity is same-directory.** `os.replace` is atomic as a POSIX rename (S288), which is
  why the writer keeps its temp file beside its output; the same page says the operation may fail
  across filesystems, so a temp under `$TMPDIR` on another device is not an atomic publish.

## Decision rule

A control receipt is **bound** when all four lines are present, the digest equals the declared
counter's blob at the freeze commit, the revision is a strict ancestor of that commit, and the
command names the declared counter. Bound and red is evidence of a failing measurement at a named
input revision. Bound and green is not evidence of anything. Unbound is `not a control`, whatever
its exit line says.
