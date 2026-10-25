source: S016 https://github.com/sahib/rmlint/blob/master/docs/rmlint.1.rst (:28, :150-153, :191-194, :431-440); S017 https://rmlint.readthedocs.io/en/latest/cautions.html (§Consider safe removal options, §Path Doubles, §Symlinks, §Hardlinks, §Collision Robustness); S018 https://codeberg.org/jbruchon/jdupes README (:249-260, :320-324); S019 https://github.com/adrianlopezroche/fdupes/blob/master/fdupes.1 (:102-104, :116-118, :131-132, :163-181); S020 https://github.com/pkolaczk/fclones/blob/main/fclones/README.md (:21-22, :241-254, :286-287); S021 https://github.com/pkolaczk/fclones/blob/main/fclones/src/dedupe.rs (:814-849, :895-902) + src/main.rs:184-186 + src/config.rs:595-604, :656-664
verified-at: 2026-10-19; fclones tag v0.35.0 (dedupe.rs 040f78e3…, main.rs b8388dcf…, config.rs fa9cfc29… — byte-identical to main @ a74f90d, sha256 compared 2026-10-19), so every dedupe.rs/main.rs/config.rs line below reads `@v0.35.0`; rmlint/jdupes/fdupes docs read at their default branch on 2026-10-19, latest releases rmlint v2.10.3, jdupes v1.31.2, fdupes v2.4.0 (W1 ART dossier §2 table, not re-verified); rmlint.1.rst sha256 8e09de1c…; jdupes README sha256 0a98212a…; fdupes.1 sha256 5398cf7c…; none of rmlint/jdupes/fdupes/fclones installed on host (souji-art.md:86)
recheck: bash -c 'u=https://raw.githubusercontent.com/pkolaczk/fclones/main/fclones/src; curl -fsSL $u/dedupe.rs | grep -c "Bail out as well if any file has been modified"; curl -fsSL $u/main.rs | grep -c "modified_before = Some(header.timestamp)"; curl -fsSL https://raw.githubusercontent.com/sahib/rmlint/master/docs/rmlint.1.rst | grep -c "WILL NOT DELETE ANY FILES"'   # expect 1 1 1

# Duplicate finders separate detection from action; act-time rechecks are narrow

## Claim
Maintained duplicate finders keep "these are duplicates" apart from "remove one", and what they recheck at act time is narrower than a content comparison:
- rmlint deletes nothing; it emits a script. Originals are designated by `//` path tagging plus `-k`/`-m`. Default matching is a hash (blake2b); byte-by-byte only with `-p`.
- fclones `group` writes a report; `remove`/`move`/`link` consume it; `--dry-run` prints the commands. At act time `partition()` re-stats each file and (a) skips non-regular files individually, (b) skips individually any file whose length differs from the group length (unless `--no-check-size`), (c) rejects the WHOLE group if any file's mtime is after `modified_before`. (c) is conditional in dedupe.rs, but main.rs defaults `modified_before` to the report header timestamp, so via the CLI it is on by default. No content re-hash or byte compare happens at act time: a same-length edit with an unchanged/rolled-back mtime passes.
- jdupes byte-verifies by default and runs change checks "immediately before scanning or taking action"; `-t` turns them off (named TOCTTOU), `-Q` skips the byte-for-byte failsafe.
- fdupes byte-compares MD5 matches (S017 §Collision Robustness); `-D` defers that confirmation "until just before file deletion" (interactive mode only); `-I` deletes as encountered and implies `--noprompt`; `--log` records the deletion choices.

## Evidence
- S016 rmlint.1.rst:28 "``rmlint`` itself WILL NOT DELETE ANY FILES." — agree.
- S016 :150 "``-a --algorithm=name`` (**default\:** *blake2b*)"; :194 "Use ``-p`` if you want byte-by-byte comparison without any hashing."
- S016 :433-435 "Don't delete any duplicates that are in tagged paths (``-k``) … (Tagged paths are those that were listed after **//**)."; :439 (`-m`) "Only look for duplicates of which at least one is in one of the tagged paths."
- S021 dedupe.rs:814 "We don't want to remove dirs or symlinks" → :819 "Skipping file {}: Not a regular file"; :826-827 length-changed file "does not belong to the group and we can safely skip it"; :843-847 "Bail out as well if any file has been modified after `config.modified_before`. We need to skip the whole group …" inside `if let Some(max_timestamp) = config.modified_before`.
- S021 main.rs:184-185 "if dedupe_config.modified_before.is_none() { dedupe_config.modified_before = Some(header.timestamp);"; config.rs:597 "If any of the files in a group was modified later, the whole group is skipped."
- S020 README:22 "There is also a `--dry-run` option that can tell you exactly what changes on the file system would be made."; :243-244 report "of `fclones group` to the standard input of `fclones remove`, `fclones move` or `fclones link`".
- S018 README:249-253 "`-t`/`--no-change-check` option disables file change checks during/after scanning. This opens a security vulnerability that is called a TOCTTOU … The program normally runs checks immediately before scanning or taking action upon a file".
- S019 fdupes.1:103-104 "defer byte-for-byte confirmation of duplicates until just before file deletion."; :117-118 "Delete duplicates as they are encountered, without grouping into sets; implies --noprompt."; :132 "Log file deletion choices to LOGFILE."

## Failure cases (Q3)
- S018 :320-324 `-Q` "performs comparisons based solely on the hashes … Do not use it on ANY data set for which any amount of data loss is unacceptable."
- S017 §Path Doubles: `fdupes -r -H --delete --noprompt dir dir` → "Oh dear, our file is gone!" (inode check is off under `-H`); §Symlinks: `ln -s dir link; fdupes -r --delete --noprompt .` → `dir/` empty; S019 :178-181 same path given twice → "all files within that directory will be listed as their own duplicates".
- S017 §Collision Robustness: two different files with equal MD5; `rmlint -a md5` schedules `rm '/home/foo/test/letter_of_rec.ps'`.
- S017 §Hardlinks: hardlinking "first deletes the duplicate and then creates a hardlink"; rdfind `-makehardlinks` on `dir dir` → `dir` empty.
- S017 §Consider safe removal options: "Rather than deleting duplicates, consider moving them to a holding area or trash folder."

## Lane link
- PROVINCE.md:12 puts "duplicate configs" in souji's scope; SKILL.md:19-23 receipt table has only `pushed`, `moved-to-obsidian`, `stale`. No class verifies identity, names an original, or rechecks content at act time.
- SKILL.md:67-70 already demands `cmp` before calling a config copy a duplicate ("Superseded-snapshot drift … `cmp` shows differing"); SKILL.md:46 re-runs the receipt at the second check.
- A souji duplicate verdict would need, at minimum: `cmp` byte equality (not a hash) between candidate and a designated original; a recorded original that is never the removal target (path-double/symlink/hardlink guards: distinct `stat -c '%d:%i'`, no symlink component); a second `cmp` at act time (fclones-style length/mtime is weaker).
- Adding a `duplicate` receipt class changes the taxonomy and tools/souji-verify.sh: OPERATOR DECISION. This entry records facts only.

## Limits
- No dupe finder was run; all behaviour is from docs and source at the cited revisions. jdupes README does not enumerate which fields its change check compares.
- rmlint's generated `remove_cmd` calls `original_check "$1" "$2"` (S017 example); its semantics are not documented in the opened sources.
- fclones `modified_before` default applies only when the report header carries a timestamp (main.rs path); library callers of `partition()` may leave it unset (reviewer's code-level reading).
