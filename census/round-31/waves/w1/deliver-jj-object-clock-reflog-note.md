# Which reflog holds the abandoned commit — r31 jj object clock

Item: SwarmExecutor08 (C3, object lifetime behind a dropped keep ref).
Fixture: `tests/fixtures/r31-jj-object-clock.sh` (delivered as `deliver-r31-jj-object-clock.sh`).
Record: `census/round-31/records/jj-object-clock-run.txt` (delivered as `deliver-jj-object-clock-run.txt`).
Measured with jj 0.45.1-7c41cdeb16b6b321c64e789a966b6adf723816a5 and git 2.56.0.

## Answer

The **HEAD reflog** holds B, and it is the only reflog that can: the repository carries exactly one
reflog file, `logs/HEAD`. In the `reflog-only` arm, B is named by one entry, `HEAD@{1}`, whose
message is `export from jj` — the entry jj's own export wrote when B was the working-copy parent.
No reflog exists for `refs/jj/keep/*`: jj writes those refs without reflogs, so `refs/jj` never
appears in a reflog listing. There is no `refs/heads` either — HEAD is detached — so the usual
`refs/heads/main` reflog is absent too. `reflog_hits` in the record therefore counts HEAD reflog
entries whose commit (`%H`) is B; with no other reflog in the repository it cannot count anything
else.

## Evidence (the `reflog-only` arm, after `jj abandon` and after the keep refs are deleted)

```
$ git reflog --all --format='%gd %H %gs'          # after jj abandon
HEAD@{0} <A> export from jj
HEAD@{1} <B> export from jj
HEAD@{2} <A> export from jj

$ git reflog --all --format='%gd %H'   (filtered to B's id)
HEAD@{1} <B>

$ find "$(git rev-parse --absolute-git-dir)/logs" -type f
logs/HEAD

$ git symbolic-ref -q HEAD || echo 'detached HEAD'
detached HEAD

$ git for-each-ref --format='%(refname)' 'refs/heads/*'
(no output: no refs/heads namespace exists)

$ after deleting every keep ref naming B or a descendant of B
keep_refs=6   reflog entries naming B=1   object_present=yes
```

Commit ids are elided as `<A>` / `<B>` because they differ between runs (jj commit ids hash the
commit time); the delivered record carries no ids at all.

## What the reflog does and does not do (from the same record)

- **It is a keeper when nothing else names B.** `reflog-only`: with every keep ref naming B or a
  descendant of B deleted and only `HEAD@{1}` left, `git gc --prune=now` kept the object
  (`reflog_hits=1 object_present=yes`); after `git reflog expire --expire=now
  --expire-unreachable=now --all` and another `git gc --prune=now` the object was gone
  (`reflog_hits=0 object_present=no`).
- **It is not load-bearing while a descendant keep ref exists.** `solo` at
  `reflog-expire-then-prune` has `reflog_hits=0` and `object_present=yes`: every reflog entry naming
  B was expired and B was still present, because a keep ref still named a descendant of B. The
  same holds in `descendant` while C is alive. Expiring the reflog is therefore neither necessary
  nor sufficient for removing the object; removing the last keep ref that names B or a descendant
  of B is what the record shows to be necessary, and `git gc --prune=now` is what then removes it.
