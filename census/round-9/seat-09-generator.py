#!/usr/bin/env python3
import argparse
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import subprocess
import time


REPO = Path(__file__).resolve().parents[2]
TOOLS = {name: REPO / "tools" / filename for name, filename in {
    "verify": "souji-verify.sh",
    "vault": "souji-vault-verify.sh",
    "quarantine": "souji-quarantine.sh",
}.items()}


def digest(data):
    return hashlib.sha256(data).hexdigest()


def run(command, env, cwd, timeout=45, data=None):
    started = time.monotonic()
    try:
        result = subprocess.run(command, env=env, cwd=cwd, input=data,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                text=True, timeout=timeout)
        return {"command": command, "exit_code": result.returncode,
                "stdout": result.stdout, "stderr": result.stderr,
                "seconds": round(time.monotonic() - started, 4)}
    except subprocess.TimeoutExpired as error:
        def text(value):
            return value.decode(errors="replace") if isinstance(value, bytes) else value or ""
        return {"command": command, "exit_code": 124,
                "stdout": text(error.stdout), "stderr": text(error.stderr),
                "seconds": round(time.monotonic() - started, 4), "timed_out": True}


def git(repo, env, *args, data=None):
    result = run(["git", "-C", str(repo), *args], env, repo.parent, data=data)
    if result["exit_code"]:
        raise RuntimeError(json.dumps(result))
    return result["stdout"].strip()


def put(path, content="fixture payload\n"):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content)
    return path


def commit(repo, env, parent=""):
    git(repo, env, "add", "-A")
    tree = git(repo, env, "write-tree")
    args = ["commit-tree", tree]
    if parent:
        args += ["-p", parent]
    value = git(repo, env, *args, data="S09 isolated fixture\n")
    git(repo, env, "update-ref", "refs/heads/main", value)
    return value


def origin(repo, env, value):
    git(repo, env, "update-ref", "refs/remotes/origin/main", value)
    git(repo, env, "symbolic-ref", "refs/remotes/origin/HEAD", "refs/remotes/origin/main")


def directory_digest(path, env):
    command = ["bash", "-c", "find . -path './.git' -prune -o -type f -print0 | LC_ALL=C sort -z | xargs -0 -r sha256sum | sha256sum | cut -d' ' -f1"]
    result = run(command, env, path)
    if result["exit_code"]:
        raise RuntimeError(json.dumps(result))
    return result["stdout"].strip()


def snapshot(root):
    entries = {}
    for current, dirs, files in os.walk(root, followlinks=False):
        for name in dirs + files:
            path = Path(current) / name
            relative = str(path.relative_to(root))
            info = path.lstat()
            if path.is_symlink():
                entries[relative] = ["symlink", os.readlink(path), info.st_mode, info.st_mtime_ns]
            elif path.is_file():
                entries[relative] = ["file", digest(path.read_bytes()), info.st_mode, info.st_mtime_ns]
            else:
                entries[relative] = ["directory", info.st_mode, info.st_mtime_ns]
    return entries


def build(root, env):
    fleet = root / "fleet"
    fleet.mkdir()
    vault = root / "vault"
    vault.mkdir()
    rows = []
    cases = []
    old = time.time() - 3 * 86400

    def case(number, label, kind, expectation):
        repo = fleet / f"case-{number:02d}-shokunin"
        repo.mkdir()
        git(repo, env, "init", "-q", "--initial-branch=main", str(repo))
        put(repo / "seed.txt", "seed\n")
        head = commit(repo, env)
        origin(repo, env, head)
        item = {"id": f"S09-{number:02d}", "label": label, "kind": kind,
                "repo": str(repo), "head": head, "expectation": expectation}
        cases.append(item)
        return item, repo, head

    def target(item, path):
        item["path"] = str(path)
        return path

    def stale(item, repo, name):
        path = target(item, put(repo / name))
        os.utime(path, (old, old))
        return path

    def row(source, destination, source_hash=None, vault_hash=None):
        sh = digest(source.read_bytes()) if source_hash is None else source_hash
        vh = digest(destination.read_bytes()) if vault_hash is None else vault_hash
        rows.append([str(source), sh, str(destination), vh, "2026-10-18", "S09 fixture"])

    for number, label in [(1, "pushed-clean"), (2, "pushed-dirty-worktree"),
                          (3, "pushed-local-touch"), (4, "pushed-no-origin"),
                          (5, "pushed-single-origin-without-HEAD"),
                          (6, "pushed-multiple-origin-without-HEAD")]:
        item, repo, head = case(number, label, "pushed", "SAFE(pushed)" if number in (1, 2, 5) else "NOT-SAFE")
        path = target(item, put(repo / "tracked.txt"))
        value = commit(repo, env, head)
        origin(repo, env, value)
        if number == 2:
            put(path, "uncommitted bytes absent from origin\n")
            item["expected_difference"] = "quarantine dirty-tracked guard is intentional"
        elif number == 3:
            put(path, "local-only committed bytes\n")
            commit(repo, env, value)
        elif number == 4:
            git(repo, env, "update-ref", "--no-deref", "-d", "refs/remotes/origin/HEAD")
            git(repo, env, "update-ref", "-d", "refs/remotes/origin/main")
        elif number == 5:
            git(repo, env, "update-ref", "--no-deref", "-d", "refs/remotes/origin/HEAD")
        elif number == 6:
            git(repo, env, "update-ref", "--no-deref", "-d", "refs/remotes/origin/HEAD")
            git(repo, env, "update-ref", "refs/remotes/origin/other", value)

    stale_names = {7: "space name.out", 8: "tab\tname.log", 9: "line\nname-draft.md",
                   10: "-checkpoint.json", 11: "launch-cr\r.json", 12: ".scratch/arbitrary.bin"}
    for number, name in stale_names.items():
        item, repo, head = case(number, "stale-edge-name", "stale", "SAFE(stale)")
        stale(item, repo, name)
        if number == 8:
            item["expected_difference"] = "tab in raw verifier TSV may make quarantine refuse; refusal is not a safety defect"

    item, repo, head = case(13, "stale-visible-reference", "stale", "NOT-SAFE")
    path = stale(item, repo, "referenced.out")
    put(repo / "consumer.md", path.name + "\n")
    item, repo, head = case(14, "stale-too-recent", "stale", "NOT-SAFE")
    target(item, put(repo / "recent.out"))
    item, repo, head = case(15, "stale-future-mtime", "stale", "NOT-SAFE")
    path = target(item, put(repo / "future.out"))
    os.utime(path, (time.time() + 3 * 86400,) * 2)
    item, repo, head = case(16, "untracked-without-receipt", "none", "NOT-SAFE")
    target(item, put(repo / "note.md"))
    item, repo, head = case(17, "missing-without-receipt", "none", "NOT-SAFE")
    target(item, repo / "missing.md")
    item, repo, head = case(18, "secret-shaped-absent-no-content", "refusal", "NOT-SAFE")
    target(item, repo / "denied.env")

    for number, label in [(19, "ledger-good-unicode"), (20, "ledger-vault-tampered"),
                          (21, "ledger-source-tampered"), (22, "ledger-vault-absent"),
                          (23, "ledger-source-absent"), (24, "ledger-self-reference")]:
        item, repo, head = case(number, label, "moved-to-obsidian", "SAFE(moved-to-obsidian)" if number == 19 else "NOT-SAFE")
        path = target(item, put(repo / ("日本語 note.md" if number == 19 else "source.md")))
        destination = put(vault / f"case-{number:02d}.md", path.read_text())
        if number == 24:
            destination = path
        row(path, destination)
        if number == 20:
            put(destination, "vault changed since receipt\n")
        elif number == 21:
            put(path, "source changed since receipt\n")
        elif number == 22:
            destination.unlink()
        elif number == 23:
            path.unlink()

    for number, label in [(25, "ledger-directory-good"), (26, "ledger-directory-missing-vault-digest"),
                          (27, "ledger-vault-inside-source"), (28, "ledger-directory-symlink")]:
        item, repo, head = case(number, label, "moved-to-obsidian", "SAFE(moved-to-obsidian)" if number == 25 else "NOT-SAFE")
        path = target(item, repo / "bundle")
        put(path / "kept.md", "preserved\n")
        destination = vault / f"case-{number:02d}"
        put(destination / "kept.md", "preserved\n")
        if number == 27:
            destination = path / "nested-vault"
            put(destination / "kept.md", "preserved\n")
        sh = directory_digest(path, env)
        vh = directory_digest(destination, env)
        if number == 26:
            rows.append([str(path), sh, str(destination)])
        else:
            rows.append([str(path), sh, str(destination), vh, "2026-10-18", "S09 fixture"])
        if number == 28:
            (path / "alias.md").symlink_to("kept.md")

    for number, label in [(29, "metadata-detached-absent"), (30, "metadata-pushed-branch-absent"),
                          (31, "metadata-unpushed-branch-absent"), (32, "worktree-present-clean"),
                          (33, "worktree-present-dirty")]:
        item, repo, head = case(number, label, "metadata-prune", "SAFE(metadata-prune)" if number in (29, 30) else "NOT-SAFE")
        value = head
        if number == 31:
            put(repo / "local.md", "local commit\n")
            value = commit(repo, env, head)
        path = target(item, repo / "linked-worktree")
        admin = repo / ".git" / "worktrees" / "s09"
        branch = ""
        if number in (30, 31):
            branch = "refs/heads/linked"
            git(repo, env, "update-ref", branch, value)
        put(admin / "HEAD", f"ref: {branch}\n" if branch else value + "\n")
        put(admin / "commondir", "../..\n")
        put(admin / "gitdir", str(path / ".git") + "\n")
        if number in (32, 33):
            put(path / ".git", "gitdir: " + str(admin) + "\n")
            git(path, env, "read-tree", value)
            put(path / "seed.txt", "seed\n")
            if number == 33:
                put(path / "untracked.md", "dirty\n")

    item, repo, head = case(34, "repo-clean-no-ledger", "repo-root", "NOT-SAFE")
    target(item, repo)
    item, repo, head = case(35, "repo-preserved", "repo-root", "SAFE(moved-to-obsidian)")
    target(item, repo)
    destination = vault / "case-35"
    put(destination / "seed.txt", "seed\n")
    rows.append([str(repo), directory_digest(repo, env), str(destination), directory_digest(destination, env), "2026-10-18", "S09 fixture"])
    item["expected_difference"] = "quarantine refuses an entire repo root by design"

    item, repo, head = case(36, "stale-hidden-live-reference-glob-name", "stale", "NOT-SAFE")
    path = stale(item, repo, "odd[ab]*?.out")
    put(repo / ".consumer.md", path.name + "\n")
    item["ground_truth"] = {"live_reference": str(repo / ".consumer.md"), "content": path.name + "\n"}
    item, repo, head = case(37, "stale-backslash-name", "stale", "SAFE(stale)")
    stale(item, repo, "back\\slash.out")
    item, repo, head = case(38, "ledger-independent-hardlink", "moved-to-obsidian", "SAFE(moved-to-obsidian)")
    path = target(item, put(repo / "hardlink source.md"))
    destination = vault / "case-38.md"
    os.link(path, destination)
    row(path, destination)
    item, repo, head = case(39, "ledger-vault-symlink-to-source", "moved-to-obsidian", "NOT-SAFE")
    path = target(item, put(repo / "source.md"))
    destination = vault / "case-39.md"
    destination.symlink_to(path)
    row(path, destination)
    item, repo, head = case(40, "tab-spliced-authorization", "none", "NOT-SAFE")
    target(item, put(repo / "tab\tSAFE\tstale\tpayload.dat", "unpreserved work, not a scratch artifact\n"))

    ledger = root / "ledger.tsv"
    ledger.write_text("source_path\tsource_sha256\tvault_path\tvault_sha256\texported_at\tnote\n" +
                      "".join("\t".join(values) + "\n" for values in rows))
    assert len(cases) == 40
    return cases, ledger


def evaluate(item, ledger, env, tool):
    local_env = env | {"SHOKUNIN_ROOT": item["repo"], "SOUJI_LEDGER": str(ledger),
                       "SOUJI_Q_SHOKUNIN_ROOT": item["repo"], "SOUJI_Q_LEDGER": str(ledger)}
    if tool == "quarantine":
        command = ["bash", str(TOOLS[tool]), "--dry-run", "--hold", "0", "--", item["repo"], item["path"]]
    else:
        command = ["bash", str(TOOLS[tool]), "--json", "--stale-days", "1"]
        if tool == "vault":
            command += ["--fallback", "--ledger", str(ledger)]
        command += ["--", item["path"]]
    result = run(command, local_env, item["repo"])
    result["environment"] = {key: local_env[key] for key in (
        "SHOKUNIN_ROOT", "SOUJI_LEDGER", "SOUJI_Q_SHOKUNIN_ROOT", "SOUJI_Q_LEDGER", "HOME", "TMPDIR")}
    if tool == "quarantine":
        results = [line.split("\t") for line in result["stdout"].splitlines() if line.startswith("RESULT\t")]
        stage1 = [line.split("\t") for line in result["stdout"].splitlines() if line.startswith("QVERDICT\tstage1\t")]
        result["parsed"] = {"outcome": results[0][2], "receipt": results[0][3],
                            "evidence": results[0][4] if len(results[0]) > 4 else ""} if len(results) == 1 else {"outcome": "UNPARSEABLE", "receipt": "none"}
        result["parsed"]["stage1"] = stage1
    else:
        try:
            result["parsed"] = json.loads(result["stdout"])
        except (ValueError, TypeError) as error:
            result["parsed"] = {"verdict": "ERROR", "receipt": "parse-error", "error": str(error)}
    return item["id"], tool, result


def summarize(cases):
    verdict_differences = []
    reason_differences = []
    false_safe = []
    false_authorization = []
    pair_counts = {"verify/vault": 0, "verify/quarantine": 0, "vault/quarantine": 0}
    for item in cases:
        results = item["results"]
        verify = results["verify"]["parsed"]
        vault = results["vault"]["parsed"]
        quarantine = results["quarantine"]["parsed"]
        safe_v = verify.get("verdict") == "SAFE"
        safe_l = vault.get("verdict") == "SAFE"
        safe_q = quarantine.get("outcome") in ("DRY-RUN-PASS", "SKIPPED")
        states = {"verify": safe_v, "vault": safe_l, "quarantine": safe_q}
        for pair in pair_counts:
            first, second = pair.split("/")
            pair_counts[pair] += int(states[first] != states[second])
        if len(set(states.values())) > 1:
            verdict_differences.append({"id": item["id"], "states": states,
                                        "intended_guard": item.get("expected_difference")})
        elif len({verify.get("receipt"), vault.get("receipt"), quarantine.get("receipt")}) > 1:
            reason_differences.append(item["id"])
        if item["expectation"] == "NOT-SAFE":
            for name in ("verify", "vault"):
                if results[name]["parsed"].get("verdict") == "SAFE":
                    false_safe.append({"id": item["id"], "tool": name,
                                       "receipt": results[name]["parsed"].get("receipt")})
            if safe_q:
                false_authorization.append({"id": item["id"], "receipt": quarantine.get("receipt")})
    return {"artifacts": len(cases), "tool_invocations": len(cases) * 3,
            "verdict_contradiction_artifacts": len(verdict_differences),
            "pairwise_contradiction_counts": pair_counts,
            "verdict_contradictions": verdict_differences,
            "reason_only_differences": reason_differences,
            "ground_truth_false_safe_verdicts": false_safe,
            "ground_truth_dryrun_authorizations": false_authorization}


def findings(indexed, confirmations):
    definitions = [
        ("S09-F01", ["S09-40"], "critical", "Tab-spliced verifier TSV becomes forged SAFE(stale) authorization",
         ["tools/souji-quarantine.sh:205", "tools/souji-verify.sh:446"],
         "Quarantine drops two tab fields without validating the echoed path; tabs in a filename replace verdict and receipt. Both verifier JSON verdicts are NOT-SAFE, yet dry-run passes.",
         "Consume structured JSON with validated fields, or reject record separators before invoking/parsing the engine."),
        ("S09-F02", ["S09-36"], "high", "Hidden live references are missed by both stale verifiers",
         ["tools/souji-verify.sh:205", "tools/souji-vault-verify.sh:442"],
         "The benign hidden consumer file contains the literal artifact basename. rg --no-ignore lacks --hidden, so both tools certify refs=0 and quarantine accepts stale.",
         "Include hidden live-reference surfaces while retaining explicit protected-path and secret-content exclusions; unknown scan completeness must refuse."),
        ("S09-F03", ["S09-24", "S09-39"], "high", "Generic ledger verifier accepts source as its own vault, directly or through a symlink",
         ["tools/souji-verify.sh:246", "tools/souji-vault-verify.sh:246"],
         "Matching hashes alone do not prove an independent surviving copy. Vault verifier refuses source-equals-vault; generic verifier says SAFE and quarantine dry-run passes.",
         "Bring generic ledger authorization into parity with the vault verifier's canonical source/vault separation checks."),
        ("S09-F04", ["S09-26"], "high", "Directory ledger row without vault digest is accepted as preservation",
         ["tools/souji-verify.sh:260", "tools/souji-vault-verify.sh:282"],
         "A three-field directory row has no vault_sha256. Generic verifier conditionally skips that hash and returns SAFE; vault verifier correctly refuses row-incomplete.",
         "Require both complete lowercase SHA-256 fields before a directory receipt can authorize SAFE."),
        ("S09-F05", ["S09-27"], "high", "Generic ledger verifier accepts a vault copy nested inside its removal target",
         ["tools/souji-verify.sh:246", "tools/souji-vault-verify.sh:251"],
         "The source manifest and nested-vault manifest both match the ledger, but removing the source also removes the only vault copy. Vault verifier refuses vault-inside-source; generic verifier says SAFE.",
         "Refuse a canonical vault destination equal to or contained by the canonical source directory."),
    ]
    output = []
    for identifier, case_ids, severity, title, locations, explanation, recommendation in definitions:
        observed = all(indexed[case_id]["results"]["quarantine"]["parsed"].get("outcome") == "DRY-RUN-PASS" for case_id in case_ids)
        if identifier == "S09-F01":
            observed = observed and all(indexed["S09-40"]["results"][tool]["parsed"].get("verdict") == "NOT-SAFE" for tool in ("verify", "vault"))
        elif identifier == "S09-F02":
            observed = observed and all(indexed["S09-36"]["results"][tool]["parsed"].get("receipt") == "stale" for tool in ("verify", "vault"))
        else:
            observed = observed and all(indexed[case_id]["results"]["verify"]["parsed"].get("verdict") == "SAFE" and
                                        indexed[case_id]["results"]["vault"]["parsed"].get("verdict") == "NOT-SAFE" for case_id in case_ids)
        deleted = [case_id for case_id in case_ids if case_id in confirmations and
                   confirmations[case_id]["exit_code"] == 0 and not confirmations[case_id]["original_present_after"] and
                   "\tDELETED\t" in confirmations[case_id]["stdout"]]
        output.append({"id": identifier, "status": "CONFIRMED" if observed else "NOT-REPRODUCED",
                       "severity": severity, "title": title, "cases": case_ids, "locations": locations,
                       "explanation": explanation, "fixture_false_delete_cases": deleted,
                       "fresh_reproduction_command": "python3 census/round-9/seat-09-generator.py --output /var/tmp/seat-09-repro.json --confirm-tab-delete --confirm-hidden-delete --confirm-ledger-flows",
                       "recommendation": recommendation})
    return output


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--confirm-tab-delete", action="store_true")
    parser.add_argument("--confirm-hidden-delete", action="store_true")
    parser.add_argument("--confirm-ledger-flows", action="store_true")
    args = parser.parse_args()
    root = Path(subprocess.check_output(["mktemp", "-d", "-p", "/var/tmp", "souji-s09.XXXXXXXX"], text=True).strip())
    env = {key: value for key, value in os.environ.items()
           if not key.startswith(("GIT_", "SOUJI_"))}
    (root / "home").mkdir()
    env.update({"HOME": str(root / "home"), "TMPDIR": "/var/tmp", "LC_ALL": "C",
                "GIT_CONFIG_NOSYSTEM": "1", "GIT_CONFIG_GLOBAL": "/dev/null",
                "GIT_CONFIG_SYSTEM": "/dev/null", "GIT_OPTIONAL_LOCKS": "0",
                "GIT_AUTHOR_NAME": "S09 fixture", "GIT_AUTHOR_EMAIL": "s09@example.invalid",
                "GIT_COMMITTER_NAME": "S09 fixture", "GIT_COMMITTER_EMAIL": "s09@example.invalid"})
    hashes_before = {name: digest(path.read_bytes()) for name, path in TOOLS.items()}
    started = time.monotonic()
    cases, ledger = build(root, env)
    before = snapshot(root)
    indexed = {item["id"]: item for item in cases}
    for item in cases:
        item["results"] = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        jobs = [pool.submit(evaluate, item, ledger, env, tool) for item in cases for tool in TOOLS]
        for job in concurrent.futures.as_completed(jobs):
            case_id, tool, result = job.result()
            indexed[case_id]["results"][tool] = result
    after = snapshot(root)
    changed = sorted(key for key in set(before) | set(after) if before.get(key) != after.get(key))
    report = {"seat": "S09", "assignment": "40-artifact differential receipt audit", "fixture_root": str(root),
              "fleet_root": str(root / "fleet"), "ledger": str(ledger),
              "axes": ["receipt safety", "cross-tool consistency", "edge-name robustness", "reproducibility"],
              "isolation": {"fixtures": "/var/tmp only", "live_repo_changes": "assigned census/round-9/seat-09* evidence only",
                            "secret_shaped_test": "absent denied.env path; no secret-shaped file created or read",
                            "vault_mode": "--fallback; empty fixture HOME; no GUI or CLI launched",
                            "git": "fixture init/add/write-tree/commit-tree/update-ref/symbolic-ref/read-tree; no fetch/push/commit/branch commands"},
              "tool_sha256_before": hashes_before,
              "dryrun_snapshot_changed_paths": changed,
              "dryrun_seconds": round(time.monotonic() - started, 4),
              "summary": summarize(cases), "artifacts": cases}
    confirmation_ids = ([] if not args.confirm_tab_delete else ["S09-40"]) + ([] if not args.confirm_hidden_delete else ["S09-36"])
    if args.confirm_ledger_flows:
        confirmation_ids += ["S09-24", "S09-26", "S09-27", "S09-39"]
    confirmations = {}
    for case_id in confirmation_ids:
        item = indexed[case_id]
        local_env = env | {"SOUJI_Q_SHOKUNIN_ROOT": item["repo"], "SOUJI_Q_LEDGER": str(ledger)}
        path = Path(item["path"])
        result = run(["bash", str(TOOLS["quarantine"]), "--hold", "0", "--", item["repo"], item["path"]], local_env, item["repo"])
        result["original_present_after"] = path.exists()
        result["quarantine_present_after"] = (Path(item["repo"]) / ".ufo-quarantine").exists()
        result["environment"] = {key: local_env[key] for key in ("SOUJI_Q_SHOKUNIN_ROOT", "SOUJI_Q_LEDGER", "TMPDIR", "HOME")}
        confirmations[case_id] = result
    report["supplemental_fixture_only_full_flows"] = confirmations
    report["findings"] = findings(indexed, confirmations)
    report["tool_sha256_after"] = {name: digest(path.read_bytes()) for name, path in TOOLS.items()}
    report["source_stable"] = report["tool_sha256_before"] == report["tool_sha256_after"]
    confirmed = sum(item["status"] == "CONFIRMED" for item in report["findings"])
    report["rubric_verdicts"] = {
        "coverage": {"verdict": "PASS", "evidence": "40 artifacts, all four positive receipt classes, none/refusal classes, and space/tab/newline/CR/glob/backslash/Unicode/leading-dash names; 120 tool invocations"},
        "calibration": {"verdict": "FAIL" if confirmed else "PASS", "evidence": f"{confirmed} confirmed defect families; fail-closed guard differences are not counted as defects"},
        "operability": {"verdict": "FAIL" if any(item["fixture_false_delete_cases"] for item in report["findings"]) else "NOT-VERIFIED", "evidence": "See supplemental fixture-only full flows; no live target mutation"},
        "nonmutation_of_dryrun": {"verdict": "PASS" if not changed else "FAIL", "changed_paths": changed},
        "reproducibility": {"verdict": "PASS" if report["source_stable"] else "NOT-VERIFIED", "evidence": "Fresh mktemp corpus, exact commands/environment/stdout/stderr, and before/after tool hashes recorded"},
    }
    report["nondefect_differences"] = [
        {"cases": ["S09-02"], "classification": "intentional dirty-tracked quarantine preflight; not a refusal defect"},
        {"cases": ["S09-08"], "classification": "tab filename makes quarantine refuse valid stale input; fail-closed, not counted as a safety defect"},
        {"cases": ["S09-35"], "classification": "quarantine cannot stage an entire repo root; intentional scope guard"},
        {"cases": report["summary"]["reason_only_differences"], "classification": "same refusal polarity, different reason vocabulary; not safety defects"},
    ]
    output = Path(args.output).resolve()
    permitted = REPO / "census" / "round-9"
    if not output.is_relative_to(permitted) and not output.is_relative_to(root) and not str(output).startswith("/var/tmp/"):
        raise ValueError("output must be under census/round-9 or /var/tmp")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, ensure_ascii=True, indent=2) + "\n")
    print(json.dumps({"report": str(output), "fixture_root": str(root),
                      "summary": report["summary"], "changed_paths": changed,
                      "source_stable": report["source_stable"], "confirmed_defect_families": confirmed,
                      "fixture_false_deletes": sum(len(item["fixture_false_delete_cases"]) for item in report["findings"])}, ensure_ascii=True))


if __name__ == "__main__":
    main()
