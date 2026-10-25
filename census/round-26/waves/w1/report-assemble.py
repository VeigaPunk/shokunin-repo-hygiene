#!/usr/bin/env python3
"""souji round 26 — report assembler (w1, ExecReportAssemble).

Reads the wave results json (when it has landed), the committed receipts under
census/round-26/records/, the round lesson, LOG.md and SCORECARD.md, and emits the
`.ufo/reports/round-26/souji.md` draft at
.ufo/waves/round-26/w1/report-rendered.md. Data absent at assembly time is rendered
as the literal marker RECEIPT-PENDING; nothing is inferred into a measurement.

  python3 -B .ufo/waves/round-26/w1/report-assemble.py            # render + self-check
  python3 -B .ufo/waves/round-26/w1/report-assemble.py --check    # check existing draft
  python3 -B .ufo/waves/round-26/w1/report-assemble.py --check FILE

Exit codes: 0 pass, 1 structural check failure, 2 usage/input refusal.

Read-only over the lane. The only write is the --out draft (never under --check).
Receipt verification runs the frozen `tools/souji-receipt-run.py verify` (read-only
git plumbing); disable with --no-verify, which then renders `verify=not-run`.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

TITLE = "# souji — Round 26 report"
REQUIRED_SECTIONS = (
    "Work performed",
    "Landed changes",
    "Before → after measurements",
    "Sources & frontier",
    "Trend verdicts",
    "SHONEN",
)
PENDING = "RECEIPT-PENDING"
BOX_RE = re.compile(r"^- \[( |x|~)\] ")
SHONEN_HEADING = "## SHONEN"
AXES = ("calibration", "operability", "coverage")


def fail(message: str, code: int = 2) -> int:
    print(f"report-assemble: {message}", file=sys.stderr)
    return code


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8", errors="replace")
    except OSError:
        return None


def cell(value: object, limit: int = 220) -> str:
    """One markdown table cell: no literal or escaped pipe, no newlines."""
    text = " ".join(str(value).replace("|", "/").split())
    if len(text) > limit:
        text = text[: limit - 3].rstrip() + "..."
    return text or "—"


def short_rev(rev: str | None) -> str:
    return rev[:7] if rev else "unknown"


def table(headers: list[str], rows: list[list[str]]) -> list[str]:
    if not rows:
        return [PENDING]
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    out.extend("| " + " | ".join(row) + " |" for row in rows)
    return out


# --------------------------------------------------------------------------- inputs


def parse_prereg(path: Path) -> dict:
    text = read_text(path) or ""
    base_match = re.search(r"Lane base:\s*([0-9a-f]{7,40})", text)
    claims: list[dict[str, str]] = []
    current: dict[str, str] | None = None
    for line in text.splitlines():
        claim = re.match(r"^CLAIM\s+(\S+)\s*$", line)
        if claim:
            current = {"claim": claim.group(1)}
            claims.append(current)
            continue
        if line.strip() == "END":
            current = None
            continue
        if current is not None:
            field = re.match(r"^(axis|surface-class|enumerate):\s*(.+?)\s*$", line)
            if field:
                current[field.group(1)] = field.group(2)
    validate = re.search(r"^\s*-?\s*K3 command:\s*(\S.*sources-census\.sh validate .*)$",
                         text, re.M)
    expected = sorted({m.group(0) for m in
                       re.finditer(r"census/round-26/records/[A-Za-z0-9._-]+\.tsv", text)})
    return {
        "text": text,
        "base": base_match.group(1) if base_match else None,
        "claims": claims,
        "validate_command": validate.group(1).strip() if validate else None,
        "expected_receipts": expected,
    }


def parse_receipt(path: Path) -> dict | None:
    text = read_text(path)
    if text is None:
        return None
    header: dict[str, str] = {}
    stdout: list[str] = []
    stderr: list[str] = []
    state = "header"
    for line in text.splitlines():
        stripped = line.strip()
        if stripped == "--- stdout ---":
            state = "stdout"
            continue
        if stripped == "--- stderr ---":
            state = "stderr"
            continue
        if state == "header":
            if "=" in line:
                key, value = line.split("=", 1)
                header[key.strip()] = value.strip()
        elif state == "stdout":
            stdout.append(line.rstrip())
        else:
            stderr.append(line.rstrip())
    keys: dict[str, str] = {}
    for line in stdout:
        match = re.match(r"^([A-Za-z][A-Za-z0-9_.-]*)=(.*)$", line)
        if match:
            keys[match.group(1)] = match.group(2).strip()
    return {
        "path": path,
        "header": header,
        "stdout": [line for line in stdout if line.strip()],
        "stderr": [line for line in stderr if line.strip()],
        "keys": keys,
    }


def receipt_verify(lane: Path, path: Path) -> tuple[str, str]:
    runner = lane / "tools" / "souji-receipt-run.py"
    if not runner.is_file():
        return "runner-absent", ""
    proc = subprocess.run(
        [sys.executable, "-B", str(runner), "verify", "--root", str(lane), str(path)],
        capture_output=True, text=True, cwd=str(lane),
    )
    if proc.returncode == 0 and "verify=ok" in proc.stdout:
        return "ok", proc.stdout.strip()
    token = (proc.stderr.strip().splitlines() or ["VERIFY-FAILED"])[0].split("\t")[0]
    return token or "VERIFY-FAILED", proc.stderr.strip()


def parse_results(path: Path) -> dict | None:
    text = read_text(path)
    if text is None:
        return None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return None
    records: list[dict] = []
    signals = 0
    signal_keys = ("status", "state", "outcome", "error", "lastError", "result")
    container = None
    if isinstance(data, dict):
        for key in ("seats", "results", "members", "agents", "items"):
            if isinstance(data.get(key), (list, dict)):
                container = data[key]
                break
        if container is None and isinstance(data.get("data"), dict):
            for key in ("seats", "results", "members"):
                if isinstance(data["data"].get(key), (list, dict)):
                    container = data["data"][key]
                    break
    else:
        container = data
    if isinstance(container, dict):
        for name, record in container.items():
            if isinstance(record, dict):
                signals += int(any(key in record for key in signal_keys))
                records.append({"name": record.get("name") or name, **record})
            else:
                signals += 1
                records.append({"name": name, "status": record})
    elif isinstance(container, list):
        for index, record in enumerate(container):
            if isinstance(record, dict):
                signals += int(any(key in record for key in signal_keys))
                records.append({"name": record.get("name") or record.get("id") or f"seat-{index}",
                                **record})
    if not records or signals == 0:
        # a swarm registry (members with kind/agentId and no status) is not a results file
        return None
    dead_words = {"dead", "failed", "failure", "error", "canceled", "cancelled",
                  "killed", "lost", "timeout", "timed_out", "aborted"}
    alive_words = {"returned", "done", "ok", "pass", "passed", "complete", "completed",
                   "idle", "published", "success"}
    seats = []
    for record in records:
        error = str(record.get("error") or record.get("lastError") or "").strip()
        status = str(record.get("status") or record.get("state") or "").strip().lower()
        if not status:
            status = "dead" if error else "unknown"
        dead = status in dead_words or bool(error)
        seats.append({
            "name": str(record.get("name")),
            "role": str(record.get("role") or "unknown"),
            "status": status,
            "agent": record.get("agentId") or record.get("agent") or "none",
            "dead": dead,
            "returned": status in alive_words and not dead,
            "error": error,
        })
    roles: dict[str, int] = {}
    for seat in seats:
        roles[seat["role"]] = roles.get(seat["role"], 0) + 1
    return {
        "path": path,
        "seats": seats,
        "roles": sorted(roles.items(), key=lambda item: (-item[1], item[0])),
        "dead": [s for s in seats if s["dead"]],
        "returned": sum(1 for s in seats if s["returned"]),
        "declared": data.get("wave") if isinstance(data, dict) else None,
    }


def parse_sections(text: str) -> dict[str, str]:
    sections: dict[str, str] = {}
    matches = list(re.finditer(r"^## (.+?)\s*$", text, re.M))
    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        sections[match.group(1)] = text[match.end():end].strip("\n")
    return sections


def bullets(body: str) -> list[str]:
    items: list[str] = []
    current: str | None = None
    for line in body.splitlines():
        if line.startswith("- "):
            if current:
                items.append(current)
            current = line[2:].strip()
        elif not line.strip():
            if current:
                items.append(current)
                current = None
        elif current is not None:
            current += " " + line.strip()
        else:
            current = line.strip()
    if current:
        items.append(current)
    return items


def paragraphs(body: str) -> list[str]:
    blocks: list[str] = []
    current: list[str] = []
    for line in body.splitlines():
        if line.strip():
            current.append(line.strip())
        elif current:
            blocks.append(" ".join(current))
            current = []
    if current:
        blocks.append(" ".join(current))
    return blocks


def parse_scorecard_axes(text: str) -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for line in text.splitlines():
        if not line.startswith("|"):
            continue
        cells = [part.strip() for part in line.strip().strip("|").split("|")]
        if len(cells) < 6 or cells[0] not in AXES:
            continue
        rows.append({"axis": cells[0], "score": cells[1],
                     "last": cells[-1], "row": line.strip()})
    return rows


def axes_region(text: str) -> str | None:
    """The ## Axes markdown table bytes (header row through the last axis row)."""
    lines = text.splitlines()
    try:
        start = next(i for i, line in enumerate(lines) if line.strip() == "## Axes")
    except StopIteration:
        return None
    block: list[str] = []
    for line in lines[start + 1:]:
        if line.startswith("|") or line.strip() == "":
            if block and not line.startswith("|"):
                break
            block.append(line)
        elif block:
            break
    return "\n".join(block).strip() or None


def git(lane: Path, *args: str) -> subprocess.CompletedProcess | None:
    try:
        return subprocess.run(["git", "-C", str(lane), "-c", "maintenance.auto=false",
                               *args], capture_output=True, text=True)
    except OSError:
        return None


def git_log(lane: Path, base: str | None) -> list[dict[str, str]] | None:
    if not base:
        return None
    proc = git(lane, "log", "--reverse", "--format=%H%x09%s", f"{base}..HEAD")
    if proc is None or proc.returncode != 0:
        return None
    rows = []
    for line in proc.stdout.splitlines():
        if "\t" in line:
            commit, subject = line.split("\t", 1)
            rows.append({"commit": commit.strip(), "subject": subject.strip()})
    return rows


def git_head(lane: Path) -> str | None:
    proc = git(lane, "rev-parse", "HEAD")
    if proc is None or proc.returncode != 0:
        return None
    return proc.stdout.strip() or None


def git_show(lane: Path, rev: str, path: str) -> str | None:
    proc = git(lane, "show", f"{rev}:{path}")
    if proc is None or proc.returncode != 0:
        return None
    return proc.stdout


def last_touch(lane: Path, path: str) -> str | None:
    proc = git(lane, "log", "-1", "--format=%h %s", "--", path)
    if proc is None or proc.returncode != 0 or not proc.stdout.strip():
        return None
    return proc.stdout.strip()


def parse_shonen(path: Path) -> list[tuple[str, str, str]]:
    text = read_text(path) or ""
    boxes: list[tuple[str, str, str]] = []
    for line in text.splitlines():
        match = re.match(r"^- \[( |x|~)\] (.+)$", line)
        if match:
            boxes.append((match.group(1), match.group(2).strip(), ""))
        elif boxes and line.startswith("  ") and line.strip():
            mark, text_, pointer = boxes[-1]
            pointer = (pointer + " " + line.strip()).strip()
            boxes[-1] = (mark, text_, pointer)
    return boxes


# --------------------------------------------------------------------------- render


def compact(receipt: dict | None, limit: int = 180) -> str:
    """A receipt's measured key=value stdout, in file order."""
    if receipt is None:
        return PENDING
    parts = ["=".join((key, value)) if value else key
             for key, value in receipt["keys"].items()]
    if not parts:
        parts = receipt["stdout"][:2]
    text = "; ".join(parts)
    if len(text) > limit:
        text = text[: limit - 3].rstrip() + "..."
    return text or PENDING


def rev_marker(receipt: dict | None) -> str:
    if receipt is None:
        return ""
    return f" @{short_rev(receipt['header'].get('rev'))}"


def render(lane: Path, prereg_path: Path, results_path: Path, receipts_dir: Path,
           lesson_path: Path, log_path: Path, scorecard_path: Path, shonen_path: Path,
           verify: bool) -> tuple[str, dict]:
    prereg = parse_prereg(prereg_path)
    scorecard_text = read_text(scorecard_path) or ""
    lesson_text = read_text(lesson_path) or ""
    lesson = parse_sections(lesson_text)
    log_text = read_text(log_path) or ""
    problems: list[str] = []

    receipts: dict[str, dict] = {}
    if receipts_dir.is_dir():
        for path in sorted(receipts_dir.glob("*.tsv")):
            parsed = parse_receipt(path)
            if parsed is not None:
                receipts[path.name] = parsed
    statuses: dict[str, str] = {}
    for name, receipt in receipts.items():
        statuses[name] = receipt_verify(lane, receipt["path"])[0] if verify else "not-run"

    head = git_head(lane)
    base = prereg["base"]
    commits = git_log(lane, base)
    results = parse_results(results_path)

    claim_rows: list[dict[str, str]] = []
    for claim in prereg["claims"]:
        name = claim["claim"]
        before = receipts.get(f"{name.lower()}-before.tsv")
        after = receipts.get(f"{name.lower()}-after.tsv")
        claim_rows.append({
            "claim": name,
            "axis": claim.get("axis", PENDING),
            "surface": claim.get("surface-class", PENDING),
            "command": claim.get("enumerate", PENDING),
            "before": compact(before) + rev_marker(before),
            "after": compact(after) + rev_marker(after),
            "verify_before": statuses.get(f"{name.lower()}-before.tsv", "no-receipt"),
            "verify_after": statuses.get(f"{name.lower()}-after.tsv", "no-receipt"),
        })

    # ---- Work performed
    work: list[str] = []
    work.append(f"Declared claims (frozen `.ufo/waves/round-26/preregistration.txt`, "
                f"lane base `{base or 'unknown'}`):")
    work.append("")
    for row in claim_rows:
        work.append(f"- **{row['claim']} — {row['axis']}** (surface-class: "
                    f"{row['surface']}): `{row['command']}`; before {row['before']}; "
                    f"after {row['after']}.")
    work.append("")
    if results and results["seats"]:
        role_mix = ", ".join(f"{role}:{count}" for role, count in results["roles"])
        work.append(f"- **W1 wave** (`{results['path']}`): seats={len(results['seats'])} "
                    f"returned={results['returned']} dead={len(results['dead'])}; "
                    f"roles={role_mix}.")
        for seat in results["dead"]:
            error = seat["error"] or "(no error text recorded)"
            if len(error) > 300:
                error = error[:297] + "..."
            work.append(f"- **Dead seat** `{seat['name']}` role={seat['role']} "
                        f"status={seat['status']}: {error}")
    else:
        registry = lane / ".ufo" / "waves" / "round-26" / "w1" / "swarm-registry.json"
        declared = PENDING
        registry_text = read_text(registry)
        if registry_text:
            try:
                members = json.loads(registry_text).get("members", {})
                declared = f"{len(members)} declared seats (registry)"
            except json.JSONDecodeError:
                declared = "registry unreadable"
        candidates = (lane / ".ufo" / "waves" / "round-26" / "w1-results.json",
                      lane / ".ufo" / "waves" / "round-26" / "w1" / "results.json")
        if results_path.is_file():
            detail = (f"`{results_path}` exists but carries no seat status records "
                      f"(not a results json)")
        elif results_path in candidates:
            detail = "no results json at " + " or ".join(f"`{p}`" for p in candidates)
        else:
            detail = f"no results json at `{results_path}`"
        work.append(f"- **W1 wave results**: {PENDING} — {detail}; "
                    f"{declared}.")
    log_entry = None
    for match in re.finditer(r"^## (.*[Rr]ound\s*26.*)$", log_text, re.M):
        log_entry = match.group(1).strip()
    if log_entry:
        work.append(f"- **LOG.md Round 26 entry**: `{log_entry}`.")
    else:
        work.append(f"- **LOG.md Round 26 entry**: {PENDING} — no Round 26 heading in "
                    f"`LOG.md` at assembly time.")
    present = ", ".join(f"§ {name}" for name in lesson) or "none"
    work.append(f"- **Lesson** (`corpus/lessons/round-26.md`): sections {present}.")
    work.append(f"- **Scope**: this assembler only reads the lane and writes one draft; "
                f"no fleet path, sibling lane, `.scratch/`, `.ufo/state/`, `MANIFEST.json`, "
                f"git index or jj state was touched. Tool installs/updates: none.")
    findings = bullets(lesson.get("Findings", ""))
    if findings:
        work.append("")
        work.append("### Findings (verbatim, reflowed, `corpus/lessons/round-26.md` § Findings)")
        work.append("")
        work.extend(f"- {item}" for item in findings)
    residuals = bullets(lesson.get("Residuals", ""))
    if residuals:
        work.append("")
        work.append("### Residuals (verbatim, reflowed, `corpus/lessons/round-26.md` § Residuals)")
        work.append("")
        work.extend(f"- {item}" for item in residuals)
    if not findings and not residuals:
        work.append(f"- Lesson Findings/Residuals: {PENDING}.")

    # ---- Landed changes
    if commits is None:
        landed = [PENDING]
    else:
        landed = table(["lane commit", "landed change"],
                       [[f"`{row['commit']}`", cell(row["subject"], 160)]
                        for row in commits])
        landed.append("")
        landed.append(f"Lane tip at assembly: `{head or 'unknown'}`.")

    # ---- Before -> after measurements
    measurements = table(
        ["claim", "axis", "before", "after", "counting command", "receipt verify"],
        [[row["claim"], row["axis"], cell(row["before"]), cell(row["after"]),
          f"`{row['command']}`",
          f"before={row['verify_before']}; after={row['verify_after']}"]
         for row in claim_rows],
    )
    measurements.append("")
    measurements.append("### Receipt inventory")
    measurements.append("")
    inventory = table(
        ["receipt", "rev", "rc", "verify", "stdout"],
        [[name, short_rev(receipt["header"].get("rev")),
          receipt["header"].get("rc", "?"), statuses.get(name, "not-run"),
          cell(compact(receipt))] for name, receipt in receipts.items()],
    )
    measurements.extend(inventory)
    missing: list[str] = []
    expected = set(prereg["expected_receipts"]) | {
        m.group(0) for m in re.finditer(r"census/round-26/records/[A-Za-z0-9._-]+\.tsv",
                                        lesson_text)}
    for path in sorted(expected):
        if Path(path).name in receipts:
            continue
        touched = last_touch(lane, path)
        detail = f"absent at tip (last touched `{touched}`)" if touched else \
            "absent at tip (no lane commit)"
        missing.append(f"- `{path}`: {PENDING} — {detail}.")
    if missing:
        measurements.append("")
        measurements.extend(missing)
    refused = [f"{name}={status}" for name, status in statuses.items() if status != "ok"]
    if verify and refused:
        measurements.append("")
        measurements.append(f"- **Receipt verify refusals**: {len(refused)} of {len(statuses)} "
                            f"receipts do not verify under the frozen "
                            f"`tools/souji-receipt-run.py verify`: "
                            f"{cell('; '.join(refused), 260)}. Resolve or disclose before "
                            f"filing; the prereg RECEIPTS lines claim `verify=ok` for each.")
    lagging = []
    for claim in prereg["claims"]:
        receipt = receipts.get(f"{claim['claim'].lower()}-after.tsv")
        rev = (receipt or {}).get("header", {}).get("rev")
        if rev and head and rev != head:
            lagging.append(f"{claim['claim']} after `{short_rev(rev)}`")
    if lagging:
        measurements.append("")
        measurements.append(f"- **After-receipt rev lag**: {', '.join(lagging)} do not match "
                            f"the lane tip `{short_rev(head)}`; the frozen after values are "
                            f"read at the landing tip, so re-run or confirm before filing.")
    measurements.append("")
    measurements.append(f"- C1 byte-diff annex (protected spans against base `{base or '?'}`): "
                        f"{PENDING} — no receipt file records it; the lesson § Receipts "
                        f"calls it a report annex.")

    # ---- Sources & frontier
    sources: list[str] = []
    if prereg["validate_command"]:
        sources.append(f"Counting command: `{prereg['validate_command']}`")
        sources.append("")
    c2_before = receipts.get("c2-before.tsv")
    c2_after = receipts.get("c2-after.tsv")
    rows_before = (c2_before or {}).get("keys", {}).get("registry_rows", PENDING)
    rows_after = (c2_after or {}).get("keys", {}).get("registry_rows", PENDING)
    on_disk = len(re.findall(r"^\|\s*S\d{3,}\s*\|", read_text(
        lane / "corpus" / "SOURCES.md") or "", re.M))
    sources.append(f"- **Registry rows**: {rows_before} → {rows_after} (c2-before/c2-after); "
                   f"on disk at assembly: {on_disk}.")
    gate_receipt = receipts.get("c2-gate.tsv")
    sources.append(f"- **Entry gate (K2)**: {compact(gate_receipt)}"
                   f"{rev_marker(gate_receipt)}; verify="
                   f"{statuses.get('c2-gate.tsv', 'no-receipt')}.")
    sources.append(f"- **Census validation (K3)**: {PENDING} — no receipt records the "
                   f"validator exit code, malformed/duplicate/enum/used-by findings and "
                   f"tier/status histograms at the tip.")
    k4 = receipts.get("c2-k4-base.tsv")
    k4_after = receipts.get("c2-k4-after.tsv")
    sources.append(f"- **Coverage agreement (K4)**: base {compact(k4)}"
                   f"{rev_marker(k4)}; tip "
                   f"{compact(k4_after) + rev_marker(k4_after) if k4_after else PENDING + ' (c2-k4-after.tsv absent)'}.")
    snapshot_dir = lane / "census" / "round-26" / "sources"
    snapshots = []
    if snapshot_dir.is_dir():
        snapshots = sorted(p.name for p in snapshot_dir.iterdir() if p.is_file())
    sums = "SHA256SUMS" if "SHA256SUMS" in snapshots else None
    sources.append(f"- **Source snapshots**: {len([s for s in snapshots if s != 'SHA256SUMS'])} "
                   f"files under `census/round-26/sources/`"
                   f"{'; bound by `SHA256SUMS`' if sums else '; no SHA256SUMS present'}.")
    f1_entries = []
    for entry in sorted((lane / "corpus" / "knowledge").glob("*.md")):
        if re.search(r"^ground:\s*F1(?:\s|—|$)", read_text(entry) or "", re.M):
            f1_entries.append(f"`corpus/knowledge/{entry.name}`")
    sources.append(f"- **F1 grounded entries at tip**: {len(f1_entries)} "
                   f"({', '.join(f1_entries) if f1_entries else 'none'}).")
    happens = (lane / "considerthese").exists()
    sources.append(f"- **`considerthese/`**: {'present' if happens else 'absent'} at the lane "
                   f"root (measured at assembly).")
    sources.append(f"- **Frontier movement**: {PENDING} — L1 verdict; the admission/refusal "
                   f"decision is recorded in the lesson § Gate below.")
    gate = paragraphs(lesson.get("Gate", ""))
    if gate:
        sources.append("")
        sources.append("### Gate (verbatim, reflowed, `corpus/lessons/round-26.md` § Gate)")
        for paragraph in gate:
            sources.append("")
            sources.append(paragraph)
    else:
        sources.append(f"- Gate decision: {PENDING} (lesson § Gate absent).")

    # ---- Trend verdicts
    axes_tip = parse_scorecard_axes(scorecard_text)
    axes_base_text = git_show(lane, base, "SCORECARD.md") if base else None
    tip_region = axes_region(scorecard_text)
    base_region = axes_region(axes_base_text) if axes_base_text else None
    if tip_region and base_region:
        if tip_region == base_region:
            axes_compare = ("identical (`axes-table` bytes at "
                            f"`{short_rev(base)}` vs `{short_rev(head)}`)")
        else:
            axes_compare = (f"CHANGED (`axes-table` bytes at `{short_rev(base)}` vs "
                            f"`{short_rev(head)}`) — C1 kill-rule protected region")
    else:
        axes_compare = PENDING
    trends: list[str] = []
    for row in axes_tip:
        trends.append(f"- **{row['axis']} ({row['score']})** — axes-table bytes: "
                      f"{axes_compare}; SCORECARD last-change cell: {cell(row['last'], 160)}.")
    if not axes_tip:
        trends.append(f"- **Axes**: {PENDING} — SCORECARD axes table unreadable.")
    trends.append(f"- **No owned-axis numeric change** (prereg AXIS-HARM GUARD; no "
                  f"re-derivable 0–10 mapping): {PENDING} — L1 confirms at filing.")
    trends.append(f"- **expansion** — {PENDING} (L1 trend judgement).")
    trends.append(f"- **quality** — {PENDING} (L1 trend judgement; lesson "
                  f"§ Residuals lists R-r26-1..R-r26-3).")
    trends.append(f"- **discernment** — {PENDING} (L1 trend judgement).")

    # ---- SHONEN
    shonen_draft = lane / ".ufo" / "waves" / "round-26" / "w1" / "shonen-lines.md"
    boxes: list[str] = []
    draft_text = read_text(shonen_draft)
    if draft_text:
        boxes = [line for line in draft_text.splitlines() if BOX_RE.match(line)]
    if len(boxes) != 4:
        boxes = []
        for mark, box_text, pointer in parse_shonen(shonen_path)[:4]:
            if pointer:
                boxes.append(f"- [{mark}] {box_text} — {PENDING} r26 pointer "
                             f"(SHONEN.md records historical: {pointer})")
            else:
                boxes.append(f"- [{mark}] {box_text} — {PENDING} (pointer to be supplied)")
    if len(boxes) != 4:
        problems.append(f"SHONEN boxes: assembled {len(boxes)} of 4")

    parts: list[str] = []
    stamp = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    parts.append(TITLE)
    parts.append("")
    parts.append(f"> Draft assembled by `.ufo/waves/round-26/w1/report-assemble.py` at {stamp} "
                 f"from the wave results json "
                 f"({'present' if results else 'absent'}), "
                 f"`census/round-26/records/`, `corpus/lessons/round-26.md`, `LOG.md` and "
                 f"`SCORECARD.md` at `{short_rev(head)}`. The L1 reviews and files the real "
                 f"report; `{PENDING}` marks data absent at assembly time.")
    for title, body in (("Work performed", work), ("Landed changes", landed),
                        ("Before → after measurements", measurements),
                        ("Sources & frontier", sources), ("Trend verdicts", trends),
                        ("SHONEN", boxes)):
        parts.append("")
        parts.append(f"## {title}")
        parts.append("")
        parts.extend(body)
    text = "\n".join(parts).rstrip() + "\n"
    meta = {"results": results is not None, "receipts": len(receipts),
            "verify": verify, "head": head, "problems": problems}
    return text, meta


# --------------------------------------------------------------------------- check


def section_body(lines: list[str], heading: str) -> list[str]:
    body: list[str] = []
    start = next((i for i, line in enumerate(lines) if line.strip() == heading), None)
    if start is None:
        return body
    for line in lines[start + 1:]:
        if line.startswith("## "):
            break
        body.append(line)
    return body


def check_report(text: str) -> list[str]:
    problems: list[str] = []
    lines = text.splitlines()
    if not any(line.strip() == TITLE for line in lines):
        problems.append(f"title missing: expected `{TITLE}`")
    for name in REQUIRED_SECTIONS:
        count = sum(1 for line in lines if line.strip() == f"## {name}")
        if count != 1:
            problems.append(f"section `## {name}` occurs {count} times (want 1)")
    shonen_like = [line for line in lines
                   if line.startswith("## SHONEN") and line.strip() != SHONEN_HEADING]
    if shonen_like:
        problems.append(f"{len(shonen_like)} extra SHONEN heading variant(s)")
    if sum(1 for line in lines if line.strip() == SHONEN_HEADING) != 1:
        problems.append("exactly one `## SHONEN` heading is required")
    # non-empty bodies, in order
    positions = []
    for name in REQUIRED_SECTIONS:
        start = next((i for i, line in enumerate(lines)
                      if line.strip() == f"## {name}"), None)
        if start is None:
            continue
        positions.append((name, start))
        body = []
        for line in lines[start + 1:]:
            if line.startswith("## "):
                break
            body.append(line)
        if not any(line.strip() for line in body):
            problems.append(f"section `## {name}` has an empty body")
    if [p[1] for p in positions] != sorted(p[1] for p in positions):
        problems.append("required sections are not in canonical order")
    shonen_body: list[str] = section_body(lines, SHONEN_HEADING)
    boxes = [line for line in shonen_body if BOX_RE.match(line)]
    if len(boxes) != 4:
        problems.append(f"SHONEN box lines: {len(boxes)} (want 4)")
    return problems


def main(argv: list[str]) -> int:
    here = Path(__file__).resolve()
    lane_default = here.parents[4]
    parser = argparse.ArgumentParser(
        description="souji round-26 report assembler (draft renderer + structural check)")
    parser.add_argument("--lane", type=Path, default=lane_default,
                        help="lane repo root (default: %(default)s)")
    parser.add_argument("--results", type=Path, default=None,
                        help="wave results json (default: .ufo/waves/round-26/w1-results.json)")
    parser.add_argument("--out", type=Path, default=None,
                        help="draft path (default: .ufo/waves/round-26/w1/report-rendered.md)")
    parser.add_argument("--check", nargs="?", const="", default=None, metavar="FILE",
                        help="check an existing draft instead of rendering")
    parser.add_argument("--no-verify", action="store_true",
                        help="skip receipt verification (renders verify=not-run)")
    args = parser.parse_args(argv)

    lane = args.lane.resolve()
    if not (lane / "SCORECARD.md").is_file() or not (lane / ".ufo").is_dir():
        return fail(f"{lane} is not a souji lane root (SCORECARD.md/.ufo missing)")

    out = args.out or (lane / ".ufo" / "waves" / "round-26" / "w1" / "report-rendered.md")
    if args.check is not None:
        target = Path(args.check).resolve() if args.check else out
        text = read_text(target)
        if text is None:
            return fail(f"cannot read draft: {target}")
        problems = check_report(text)
        for problem in problems:
            print(f"PROBLEM {problem}")
        boxes = sum(1 for line in section_body(text.splitlines(), SHONEN_HEADING)
                    if BOX_RE.match(line))
        print(f"check={'PASS' if not problems else 'FAIL'} file={target} "
              f"sections={len(REQUIRED_SECTIONS)} shonen="
              f"{sum(1 for line in text.splitlines() if line.strip() == SHONEN_HEADING)} "
              f"boxes={boxes} problems={len(problems)}")
        return 0 if not problems else 1

    results = args.results
    if results is None:
        candidates = (lane / ".ufo" / "waves" / "round-26" / "w1-results.json",
                      lane / ".ufo" / "waves" / "round-26" / "w1" / "results.json")
        results = next((path for path in candidates if path.is_file()), candidates[0])
    text, meta = render(
        lane,
        lane / ".ufo" / "waves" / "round-26" / "preregistration.txt",
        results.resolve(),
        lane / "census" / "round-26" / "records",
        lane / "corpus" / "lessons" / "round-26.md",
        lane / "LOG.md",
        lane / "SCORECARD.md",
        lane / "SHONEN.md",
        verify=not args.no_verify,
    )
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    problems = check_report(text) + meta["problems"]
    boxes = sum(1 for line in section_body(text.splitlines(), SHONEN_HEADING)
                if BOX_RE.match(line))
    for problem in problems:
        print(f"PROBLEM {problem}")
    print(f"rendered={out} results={'present' if meta['results'] else 'absent'} "
          f"receipts={meta['receipts']} verify={'on' if meta['verify'] else 'off'} "
          f"sections={len(REQUIRED_SECTIONS)} "
          f"shonen={sum(1 for line in text.splitlines() if line.strip() == SHONEN_HEADING)} "
          f"boxes={boxes} check={'PASS' if not problems else 'FAIL'} problems={len(problems)}")
    return 0 if not problems else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
