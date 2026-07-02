---
name: execute-issues
description: Execute GitHub issues for a version or phase sequentially - implement, validate, commit, push, and generate a report.
---

# Skill: Execute GitHub Issues

Execute GitHub issues for a version or phase sequentially: implement, validate, commit, push, and generate a report.

## Usage

```
/execute-issues <label> [--phase vA.B] [--issue NADI-xxx] [--dry-run]
```

The `<label>` is the GitHub version label exactly as it appears (e.g., `v0::version:0`).

- `/execute-issues v0::version:0` -- execute all open issues labeled `v0::version:0`, phase by phase
- `/execute-issues v0::version:0 --phase v0.2` -- execute only that phase's issues
- `/execute-issues v0::version:0 --issue NADI-003` -- execute a single issue from that version
- `/execute-issues v0::version:0 --dry-run` -- show execution plan without making changes

## Instructions

### Step 0: Verify prerequisites

1. Confirm we are on the expected branch (e.g., `main` or the user's working branch)
2. Confirm working tree is clean (`git status`)
3. Confirm `gh` is authenticated
4. Parse the label to determine version:
   - Label `v0::version:0` -> version `A=0`
5. Fetch issues from GitHub:
   ```bash
   gh issue list --label "{label}" --state open --limit 100
   ```
6. Read the phase issues files for detailed descriptions: `spec/roadmap/implementation/v{A}.{B}-issues.md` (one per phase of the version; only the `--phase` one if given)
7. If GitHub reports exist (`spec/roadmap/implementation/v{A}.{B}-github-report.md`), read the NADI-to-GitHub# mapping
8. Read [spec/ROADMAP.md](../../../spec/ROADMAP.md) for the version goal and the phase (`vA.B`) DoD, [spec/ARCHITECTURE.md](../../../spec/ARCHITECTURE.md) for the invariants and contracts the issue must honor (tick phase order, RNG discipline, Nadi delivery, predation rules, the snapshot schema, testing/CI), and [spec/MISSION.md](../../../spec/MISSION.md) for the development principles

### Step 1: Build execution queue

From the GitHub issue list, build an ordered queue based on dependencies:
- Parse NADI-xxx IDs from issue titles (format: `NADI-xxx: {title}`)
- Determine dependency order from the phase issues files' dependency trees (phases execute in roadmap order: v0.1 before v0.2, etc.)
- Issues with no unmet dependencies go first
- Skip issues already closed on GitHub
- If `--issue NADI-xxx` is specified, execute only that issue (but verify its dependencies are closed)

Show the user the execution plan and ask for confirmation.

### Step 2: Execute each issue (loop)

For each issue in the queue:

#### 2a. Assign and announce

Print: `--- Starting NADI-xxx: {title} ---`

#### 2b. Read issue details

Read the full issue description from the phase issues file (the detailed section for this NADI-xxx).

#### 2c. Implement

Execute the tasks described in the issue. Follow the project conventions in `CLAUDE.md` and the principles in `spec/MISSION.md`. Route by component:

- **Engine changes** (`nadiloka/`): World/Meru, Tejas, the Nadi bus, Digitant/brain, the Jati loader, renderers, the snapshot serializer/server. The engine honors the invariants in ARCHITECTURE §Key invariants and pitfalls: fixed five-phase tick order, one World-owned seeded `random.Random` (module-level `random.*` forbidden), snapshot iteration, deferred Nadi delivery in deterministic order, the pysm rules (cargo not `input=`, manual initial `on_enter`, internal transitions), no double-eat.
- **Species changes** (`species/*.yaml`): Jati descriptors only. Adding or changing a species must need NO engine change — if it does, the abstraction is leaking; stop and surface it.
- **Demo changes** (`demos/`): runnable per-phase scenarios; parameters live in the world config, seeds always explicit (`--seed`).
- **Web changes** (`web/`, `nadiloka/snapshot.py`, `nadiloka/server.py`): the observation layer is strictly read-only over the world — no write path into the tick; FastAPI/uvicorn/Node stay optional dependencies the engine never imports.
- **Contract changes:** any change to a stable seam (the tick phase order, the Nadi message/delivery semantics, the Jati descriptor fields, the snapshot schema, the counter set) updates `spec/ARCHITECTURE.md` **AND** its contract/pinning test, in the same commit.
- Follow existing code style and patterns; keep each version self-contained (don't pull later-version concerns in early — one idea per version). The hot body-tick stays pure cheap arithmetic — no heavy computation, no LLM calls. No emoji anywhere.

#### 2d. Validate

Run validation checks (Python only — the optional web client validates separately in `web/`):

1. **Unit + pinning tests:** `pytest` for the changed modules (unit, plus the tests that pin the invariants: pysm pitfalls, RNG discipline, delivery order, snapshot iteration)
2. **Determinism harness:** two runs with the same seed and config produce byte-identical counter logs (ARCHITECTURE §Testing and CI)
3. **Smoke run:** the current phase's fixed-seed K-tick run stays inside its configured band (no explosion, no extinction) — this encodes the phase DoD
4. **Lint:** `ruff check {changed paths}`
5. **Syntax/import (Python):** `python3 -m py_compile {changed_py_files}` and an import check for changed modules
6. **Acceptance criteria:** go through each criterion from the issue and verify against the phase DoD in ROADMAP.md

Record pass/fail for each check. **Tests are part of the work** — a feature lands with the tests that encode its acceptance (see ARCHITECTURE §Testing and CI). CI needs no network, no Node, no pygame; if the issue touches `web/`, run its frontend tests (fixture-snapshot render) separately.

#### 2e. Commit

```bash
git add {specific files created/modified}
git commit -m "$(cat <<'EOF'
NADI-xxx: {title}

{1-2 sentence summary of what was implemented}

Closes #{github-issue-number}

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
```

#### 2f. Push

```bash
git push
```

#### 2g. Close issue with summary

```bash
gh issue close {issue-number} --comment "$(cat <<'EOF'
## Implementation Summary

**Commit:** {commit-hash}
**Files changed:** {count}

### What was done
{bullet list of key changes}

### Validation
{pass/fail status for each check}

### Acceptance criteria
{checklist with pass/fail}
EOF
)"
```

#### 2h. Tick the roadmap checklist and log progress

Mark the issue done in the phase's **Implementation plan** checklist in `spec/ROADMAP.md` (`- [ ] NADI-xxx ...` -> `- [x] NADI-xxx ...`); include this edit in the issue's commit (or a follow-up docs commit at phase end).

Append to the in-memory execution log:
- Issue ID, title
- Commit hash
- Files changed (list)
- Validation results (including test pass/fail)
- Status: success/partial/failed

### Step 3: Handle failures

If implementation or validation fails for an issue:

1. Do NOT commit broken code
2. Stash or revert changes: `git checkout -- .`
3. Add a comment to the GitHub issue explaining what failed
4. Log the failure
5. Ask the user: continue to next issue (if no dependency), or stop?

### Step 3b: Version bump on completion

**Do NOT bump the version automatically.** Never change the version (VERSION file, RELEASE.txt, or git tag) without explicit user confirmation. When a phase's issues are all done, report completion and let the user decide whether/when to release via `/release-version`.

Version notation `A.B.C`: `A` = roadmap version (v0→0 … v6→6), `B` = phase within it, `C` = a post-release fix on that phase. Roadmap phase `vA.B` → semver `A.B.0` (e.g. v0.2 → `0.2.0`). Releases are cut per phase. If the user confirms a release, delegate to `/release-version`.

If some issues failed or were skipped, do NOT bump the version. Note in the execution report that the phase is incomplete.

### Step 4: Generate execution report

After all of a phase's issues are processed (or on stop), generate:
`spec/roadmap/implementation/v{A}.{B}-execution-report.md`

```markdown
# Phase v{A}.{B} -- Execution Report

**Date:** {date}
**Branch:** {branch name}
**Label:** {label}
**Target version:** {A.B.0}
**Executed by:** Claude Code

## Summary

| Status | Count |
|--------|-------|
| Completed | {n} |
| Failed | {n} |
| Skipped | {n} |
| Remaining | {n} |

## Issues

| # | NADI ID | Title | Phase | Status | Commit | Files | Tests |
|---|---------|-------|-------|--------|--------|-------|-------|
| 1 | NADI-001 | Project skeleton & tooling | v0.1 | completed | a1b2c3d | 4 | pass |
| ... | ... | ... | ... | ... | ... | ... | ... |

## Detailed Results

### NADI-001: Project skeleton & tooling

**Status:** completed
**Commit:** a1b2c3d
**Files changed:**
- `nadiloka/...` (added)

**Validation:**
- [x] Unit + pinning tests: pass
- [x] Determinism harness: pass
- [x] Smoke run: pass
- [x] Lint (ruff): pass
- [x] Acceptance criteria: all pass

---

### NADI-002: ...

## Next Steps

{List of remaining issues not yet executed, with their dependencies}
```

Commit and push this report:

```bash
git add spec/roadmap/implementation/v{A}.{B}-execution-report.md
git commit -m "$(cat <<'EOF'
Add v{A}.{B} execution report

{n} issues completed, {n} failed, {n} remaining.

Co-Authored-By: Claude <noreply@anthropic.com>
EOF
)"
git push
```

## Important Rules

- **One issue at a time.** Never work on multiple issues simultaneously.
- **Dependency order.** Never start an issue whose dependencies are not closed.
- **Clean commits.** Each issue = one commit. No mixing work across issues.
- **No broken code.** Only commit code that passes validation (tests + ruff included).
- **Tests ship with the feature.** Every issue lands with the tests that encode its acceptance — no "tests later." No network, Node, or pygame in the Python test suite.
- **Determinism is sacred.** Fixed phase order, one World-owned seeded RNG (no module-level `random.*`), snapshot iteration, deferred Nadi delivery in stable order. The determinism harness must pass on every issue.
- **Declarative over code.** New species and behaviours are Jati descriptors, never engine edits. An engine change forced by a species is an abstraction leak — surface it, don't paper over it.
- **Bus-only interaction.** Agents communicate only through Nadi messages; no direct agent-to-agent references in behaviour logic.
- **Cheap body-tick.** The hot loop stays pure arithmetic — no heavy computation, no LLM calls.
- **Observation is read-only.** Renderers, counters, and the web server never mutate the world; toggling them never changes a run.
- **Contracts stay stable.** A seam change updates spec/ARCHITECTURE.md and its pinning test in the same commit.
- **No emoji** anywhere: code, docs, output (project convention).
- **Ask on ambiguity.** If an issue description is unclear, ask the user rather than guessing.
- **Progress updates.** Print a short status line after each issue completes; keep the ROADMAP implementation-plan checkboxes in sync.
