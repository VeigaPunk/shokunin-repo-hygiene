#!/usr/bin/env python3
"""mirror-build.py — build the round-26 C2 scratch census mirror, then validate it.

The frozen contract (.ufo/waves/round-26/preregistration.txt, C2 SCRATCH MIRROR
GATE) requires, BEFORE the first real registry append:

    a copy of corpus/ plus the append block plus the admitted entries, then
    scripts/sources-census.sh validate --file <mirror>/corpus/SOURCES.md
    must exit 0 (warnings allowed).

This tool performs exactly that, in that order. The lane corpus is opened
read-only: the copy is what receives the appended rows, and the admitted
entries are dropped at their repo-relative paths INSIDE the copy, because
sources-census.sh resolves `used-by` against the parent of the file's parent
(the mirror root) — so a mirror whose entries are missing reports E11.

Usage:
    python3 -B mirror-build.py --entries-dir DIR --rows-file FILE
                               [--corpus DIR] [--dest DIR] [--force]
                               [--validate SCRIPT]
                               [--entry NAME[=REPO/REL/PATH]]...

    --entries-dir  directory holding the final admitted-entry bytes
    --rows-file    the normalized append block (one markdown row per line)
    --corpus       source corpus to copy (default: the lane's corpus/)
    --dest         mirror root (default: /var/tmp/souji-r26-mirror); must live
                   under /var/tmp or inside the lane repo
    --force        replace a previous mirror this tool built (marker-checked)
    --expect-rows-before N
                   registry rows required before the append; default 127 is the
                   frozen C2 base literal, 0 disables the binding
    --entry        map a draft basename to a repo-relative path; supplying any
                   --entry replaces the default two-entry mapping, so renamed
                   drafts are always explicit

Order of work: parse and statically check the append block, hash the source
registry, copy corpus/, drop the entries, resolve used-by against the mirror,
insert the rows, check entry citations, run the validate command. Every
refusal happens before a mirror is created, and nothing is written to the
source corpus (its digest is re-checked after the build).

Output is a receipt: mirror/source paths, rows_before/rows_appended/rows_after,
ids_appended, rows_sha256, source_registry_sha256, mirror_registry_sha256, one
entry line plus entry_sha256 per admitted entry, WARN lines, the validate
command's own stdout, and `validate_exit=<n>`.

Append-block contract (rejects; it never repairs a row):
  * exactly the five ids S128 S129 S130 S131 S132, ascending, no duplicate,
    none already present in the registry;
  * 11 non-empty cells and NF=13 on '|' split, with no literal or escaped
    pipe inside a cell (the C2 kill rule);
  * status mined; tier A|B|C; kind in the census enum; opened an ISO date not
    in the future; recheck ISO date, NNd, or symbolic cadence; recheck is
    never empty;
  * used-by is '—' or a comma list of repo-relative paths, each one of the
    entries this run drops and each resolving on disk in the mirror.

Entry contract: every `source: S<id>` citation in a dropped entry must resolve
in the post-append registry (a citation of a row that is not appended is a C2
kill). A missing `ground: F1` front-matter line is reported as a WARN, not a
refusal, because K1 is the frozen counter for that.

Exit: 0 mirror built and validate exited 0; 1 build/integrity refusal;
2 usage/environment; otherwise the validate exit code, which is always printed
as `validate_exit=<n>`.
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import re
import shutil
import subprocess
import sys
from pathlib import Path

LANE = Path("/home/vgpnk/Projects/shokunin/souji-shokunin")
DEFAULT_CORPUS = LANE / "corpus"
DEFAULT_DEST = Path("/var/tmp/souji-r26-mirror")
DEFAULT_VALIDATE = Path("/home/vgpnk/Projects/shokunin/scripts/sources-census.sh")

MARKER = ".souji-mirror-build"
EXPECTED_IDS = ("S128", "S129", "S130", "S131", "S132")
DEFAULT_ENTRIES = (
    "git-auto-maintenance-trigger-set.md",
    "git-auto-maintenance-trigger-set-r23.md",
)
ALLOWED_ROOT = (Path("/var/tmp"), LANE)

HEADER_CELLS = (
    "id", "source", "kind", "tier", "scope", "anchor",
    "teaches", "status", "opened", "recheck", "used-by",
)
KINDS = {"spec", "docs", "paper", "code", "tool", "dataset", "talk", "book",
         "community", "own-work"}
TIERS = {"A", "B", "C"}

ID_RE = re.compile(r"^S[0-9]{3,}$")
ISO_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
CADENCE_RE = re.compile(r"^([0-9]+d|[A-Za-z][A-Za-z0-9 _-]*)$")
SOURCE_RE = re.compile(r"^\s*(?:[-*]\s*)?source:\s*(S[0-9]{3,})", re.M)
GROUND_RE = re.compile(r"^ground:\s*F1\b", re.M)
HEADING_RE = re.compile(r"^ {0,3}##[ \t]+Registry[ \t]*$")
ANY_HEADING_RE = re.compile(r"^ {0,3}#{1,6}[ \t]")
ROW_RE = re.compile(r"^ {0,3}\|")
ID_SCAN_RE = re.compile(r"^ {0,3}\|[ \t]*(S[0-9]{3,})[ \t]*\|")

warnings: list[str] = []


def die_usage(msg):
    print(f"mirror-build: {msg}", file=sys.stderr)
    raise SystemExit(2)


def die_build(msg):
    print(f"mirror-build: REFUSED: {msg}", file=sys.stderr)
    raise SystemExit(1)


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def parse_rows(path: Path) -> list[list[str]]:
    """Strictly parse the append block; return the 11 cell lists per row."""
    text = path.read_text(encoding="utf-8")
    rows: list[list[str]] = []
    seen: set[str] = set()
    for lineno, raw in enumerate(text.splitlines(), 1):
        line = raw.rstrip("\r")
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        where = f"{path}:{lineno}"
        if line != line.strip():
            die_build(f"{where}: row has leading/trailing whitespace")
        if not (line.startswith("|") and line.endswith("|")):
            die_build(f"{where}: row must start and end with '|'")
        if "\\|" in line:
            die_build(f"{where}: escaped pipe inside a cell (C2 kill rule)")
        if len(line.split("|")) != 13:
            die_build(f"{where}: NF={len(line.split('|'))} (want 13)")
        cells = [c.strip() for c in line.split("|")[1:-1]]
        if len(cells) != 11:
            die_build(f"{where}: {len(cells)} cells (want 11)")
        for idx, cell in enumerate(cells):
            if not cell:
                die_build(f"{where}: empty cell {HEADER_CELLS[idx]}")
            if "|" in cell:
                die_build(f"{where}: literal pipe in cell {HEADER_CELLS[idx]}")
        rid = cells[0]
        if not ID_RE.match(rid):
            die_build(f"{where}: id {rid!r} is not S[0-9]{{3,}}")
        if rid in seen:
            die_build(f"{where}: duplicate id {rid} in the append block")
        seen.add(rid)
        rows.append(cells)

    if not rows:
        die_build(f"{path}: append block is empty")
    ids = [r[0] for r in rows]
    if ids != sorted(ids):
        die_build(f"{path}: ids not ascending: {ids}")
    if tuple(ids) != EXPECTED_IDS:
        die_build(f"{path}: ids {ids} != frozen renumber target {list(EXPECTED_IDS)}")
    return rows


def check_row_static(rows: list[list[str]], today: datetime.date) -> None:
    for cells in rows:
        rid = cells[0]
        kind, tier, status = cells[2], cells[3], cells[7]
        opened, recheck = cells[8], cells[9]
        if kind not in KINDS:
            die_build(f"{rid}: kind={kind!r} not in the census enum")
        if tier not in TIERS:
            die_build(f"{rid}: tier={tier!r} not A|B|C")
        if status != "mined":
            die_build(f"{rid}: status={status!r} (frozen contract: mined)")
        if not ISO_RE.match(opened):
            die_build(f"{rid}: opened={opened!r} not an ISO date")
        try:
            opened_date = datetime.date.fromisoformat(opened)
        except ValueError:
            die_build(f"{rid}: opened={opened!r} is not a real date")
        if opened_date > today:
            die_build(f"{rid}: opened={opened} is in the future")
        if not CADENCE_RE.match(recheck):
            die_build(f"{rid}: recheck={recheck!r} is not ISO/NNd/symbolic")


def check_used_by(rows: list[list[str]], entry_paths: set[str],
                  mirror: Path) -> None:
    for cells in rows:
        rid, usedby = cells[0], cells[10]
        if usedby == "—":
            continue
        for rel in (p.strip() for p in usedby.split(",")):
            if not rel:
                die_build(f"{rid}: empty used-by element")
            if rel.startswith("/") or ".." in Path(rel).parts:
                die_build(f"{rid}: used-by {rel!r} is not repo-relative")
            if rel not in entry_paths:
                die_build(
                    f"{rid}: used-by {rel!r} is not one of the admitted entries "
                    f"{sorted(entry_paths)}")
            if not (mirror / rel).is_file():
                die_build(f"{rid}: used-by {rel!r} missing in the mirror")


def insert_rows(lines: list[str], rows: list[list[str]]) -> list[str]:
    start = next((i for i, ln in enumerate(lines)
                  if HEADING_RE.match(ln.rstrip("\n"))), None)
    if start is None:
        die_build("no '## Registry' heading in corpus/SOURCES.md")
    last = None
    for j in range(start + 1, len(lines)):
        stripped = lines[j].rstrip("\n")
        if ANY_HEADING_RE.match(stripped):
            break
        if ROW_RE.match(stripped):
            last = j
    if last is None:
        die_build("no table row inside the '## Registry' section")
    rendered = ["| " + " | ".join(cells) + " |\n" for cells in rows]
    return lines[:last + 1] + rendered + lines[last + 1:]


def scan_ids(lines: list[str]) -> list[str]:
    ids: list[str] = []
    for ln in lines:
        m = ID_SCAN_RE.match(ln.rstrip("\n"))
        if m:
            ids.append(m.group(1))
    return ids


def resolve_dest(dest: Path, corpus: Path) -> Path:
    r = dest.resolve()
    lane = LANE.resolve()
    c = corpus.resolve()
    if r == lane:
        die_build(f"dest {r} is the lane repository root")
    if r == c or r.is_relative_to(c) or c.is_relative_to(r):
        die_build(f"dest {r} overlaps the source corpus {c}")
    if not any(r == a.resolve() or r.is_relative_to(a.resolve()) for a in ALLOWED_ROOT):
        die_build(f"dest {r} is outside /var/tmp and the lane repo (hard bound)")
    return r


def prepare_dest(dest: Path, force: bool) -> None:
    if dest.exists():
        if not dest.is_dir():
            die_build(f"dest {dest} exists and is not a directory")
        if not any(dest.iterdir()):
            return
        if not (dest / MARKER).is_file():
            die_build(f"dest {dest} is non-empty and carries no {MARKER} marker")
        if not force:
            die_build(f"dest {dest} holds a previous mirror; pass --force to replace")
        shutil.rmtree(dest)
    dest.mkdir(parents=True)


def entry_sources(entry: Path) -> list[str]:
    return SOURCE_RE.findall(entry.read_text(encoding="utf-8"))


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser(add_help=True, description=__doc__.split("\n")[0])
    ap.add_argument("--entries-dir", required=True)
    ap.add_argument("--rows-file", required=True)
    ap.add_argument("--corpus", default=str(DEFAULT_CORPUS))
    ap.add_argument("--dest", default=str(DEFAULT_DEST))
    ap.add_argument("--validate", default=str(DEFAULT_VALIDATE))
    ap.add_argument("--force", action="store_true")
    ap.add_argument("--expect-rows-before", type=int, default=127,
                    metavar="N",
                    help="registry rows required before the append (0 disables); "
                         "default 127 is the frozen C2 base literal")
    ap.add_argument("--entry", action="append", default=[],
                    metavar="NAME[=REPO/REL/PATH]")
    args = ap.parse_args(argv)

    corpus = Path(args.corpus).resolve()
    entries_dir = Path(args.entries_dir).resolve()
    rows_file = Path(args.rows_file).resolve()
    validate = Path(args.validate).resolve()

    if not (corpus / "SOURCES.md").is_file():
        die_usage(f"no corpus/SOURCES.md under {corpus}")
    if not entries_dir.is_dir():
        die_usage(f"--entries-dir is not a directory: {entries_dir}")
    if not rows_file.is_file():
        die_usage(f"--rows-file not found: {rows_file}")
    if not validate.is_file():
        die_usage(f"--validate script not found: {validate}")

    mapping: dict[str, str] = {} if args.entry else {
        n: f"corpus/knowledge/{n}" for n in DEFAULT_ENTRIES}
    for spec in args.entry:
        name, sep, rel = spec.partition("=")
        name = name.strip()
        if not name:
            die_usage(f"--entry needs a basename: {spec!r}")
        rel = rel.strip() if sep else f"corpus/knowledge/{name}"
        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            die_usage(f"--entry {name}: {rel!r} is not repo-relative")
        if rel_path.parts[:1] != ("corpus",):
            die_usage(f"--entry {name}: {rel!r} must live under corpus/")
        mapping[name] = rel

    if len(mapping) != 2:
        die_usage(f"exactly 2 admitted entries are required, got {len(mapping)}")

    for name in mapping:
        if not (entries_dir / name).is_file():
            die_build(f"admitted entry missing from --entries-dir: {name}")
    extra = sorted(p.name for p in entries_dir.glob("*.md") if p.name not in mapping)
    if extra:
        warnings.append(f"entries-dir also holds non-mapped markdown: {extra}")

    dest = resolve_dest(Path(args.dest), corpus)
    today = datetime.datetime.now(datetime.UTC).date()
    rows = parse_rows(rows_file)
    check_row_static(rows, today)

    source_digest = sha256(corpus / "SOURCES.md")
    prepare_dest(dest, args.force)
    (dest / MARKER).write_text(
        "souji round-26 C2 scratch mirror; built by mirror-build.py\n"
        f"source_corpus={corpus}\nrows_file={rows_file}\n", encoding="utf-8")

    plan = Path(dest) / "corpus"
    shutil.copytree(corpus, plan, symlinks=True)

    entry_paths: set[str] = set()
    for name, rel in mapping.items():
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(entries_dir / name, target)
        entry_paths.add(rel)

    check_used_by(rows, entry_paths, dest)

    registry = plan / "SOURCES.md"
    lines = registry.read_text(encoding="utf-8").splitlines(keepends=True)
    before_ids = scan_ids(lines)
    if args.expect_rows_before and len(before_ids) != args.expect_rows_before:
        die_build(
            f"registry holds {len(before_ids)} rows, not the frozen base literal "
            f"{args.expect_rows_before}; build the mirror from the base bytes "
            f"(pass --expect-rows-before 0 only to disable this binding)")
    clash = sorted(set(before_ids) & {c[0] for c in rows})
    if clash:
        die_build(f"append block repeats registry ids: {clash}")
    after_lines = insert_rows(lines, rows)
    registry.write_text("".join(after_lines), encoding="utf-8")

    if sha256(corpus / "SOURCES.md") != source_digest:
        die_build(f"source registry changed during the build: {corpus}")

    appended_ids = [c[0] for c in rows]
    known = set(before_ids) | set(appended_ids)
    for name, rel in mapping.items():
        entry = dest / rel
        cited = sorted(set(entry_sources(entry)))
        if not cited:
            die_build(f"{rel}: carries no 'source: S<id>' citation")
        dangling = [sid for sid in cited if sid not in known]
        if dangling:
            die_build(f"{rel}: cites rows not in the post-append registry: {dangling}")
        if not GROUND_RE.search(entry.read_text(encoding="utf-8")):
            warnings.append(f"{rel}: no 'ground: F1' line (C2 K1 will score 0)")

    print(f"mirror={dest}")
    print(f"source_corpus={corpus}")
    print(f"rows_before={len(before_ids)}")
    print(f"rows_appended={len(rows)}")
    print(f"rows_after={len(scan_ids(after_lines))}")
    print(f"ids_appended={','.join(appended_ids)}")
    print(f"rows_sha256={sha256(rows_file)}")
    print(f"source_registry_sha256={source_digest}")
    print(f"mirror_registry_sha256={sha256(registry)}")
    print(f"entries={len(mapping)}")
    for name in sorted(mapping):
        print(f"entry {mapping[name]}")
        print(f"entry_sha256 {mapping[name]} {sha256(dest / mapping[name])}")
    for warning in warnings:
        print(f"WARN {warning}")

    proc = subprocess.run(
        ["bash", str(validate), "validate", "--file", str(registry)],
        text=True, capture_output=True,
    )
    if proc.stdout:
        sys.stdout.write(proc.stdout)
    if proc.stderr:
        sys.stderr.write(proc.stderr)
    print(f"validate_exit={proc.returncode}")
    return 0 if proc.returncode == 0 else proc.returncode


if __name__ == "__main__":
    try:
        sys.exit(main(sys.argv[1:]))
    except SystemExit:
        raise
    except BrokenPipeError:
        sys.exit(1)
