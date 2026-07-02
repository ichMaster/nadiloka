---
name: upload-issues
description: Upload issues from a phase issues file to GitHub one by one with proper labels and dependencies.
---

# Skill: Upload Phase Issues to GitHub

Upload issues from a phase issues file to GitHub one by one, with proper labels (prefixed by version) and dependencies.

## Usage

```
/upload-issues <phase-issues-file>
```

Example: `/upload-issues @spec/roadmap/implementation/v0.1-issues.md`

A phase issues file is the fine-grained breakdown of a ROADMAP phase (`vA.B`): each phase in [spec/ROADMAP.md](../../../spec/ROADMAP.md) is split into `NADI-xxx` issues (the same list appears as the phase's **Implementation plan** checklist in the roadmap). If the file does not exist yet, derive it from the phase's Goal / Tasks / DoD / Tests first (following the format of the existing `vA.B-issues.md` files), then run this skill.

## Instructions

### Step 1: Read the phase issues file

Read the provided file (e.g., `spec/roadmap/implementation/v0.1-issues.md`).

Determine from the file:
- **Version number** (A) and **phase** (A.B): from the filename or heading (e.g., `v0.1-issues.md` -> version `0`, phase `v0.1`)
- **Label prefix**: `v{A}::` (e.g., `v0::`)

Parse the **Issues Summary Table** to extract for each issue:
- `ID` (e.g., NADI-001)
- `Title`
- `Size` (S, M, L)
- `Phase` (e.g., `v0.1`)
- `Dependencies` (list of NADI-xxx IDs; may reference earlier phases)

Then parse each **detailed issue section** (heading with NADI-xxx) to extract:
- `Description`
- `What needs to be done` (full content)
- `Dependencies`
- `Expected result`
- `Acceptance criteria` (checklist — should align with the phase DoD in ROADMAP.md)

Infer the **Area** for each issue from the components it touches (the summary table has no Area column): `engine` (`nadiloka/`), `species` (`species/*.yaml`), `demos` (`demos/`), `web` (`web/` + `snapshot.py`/`server.py`), `tests` (test-only work).

### Step 2: Confirm with user

Show the user a summary of what will be created:
- Number of issues
- Label prefix (e.g., `v0::`)
- Full list of labels that will be created
- Ask for confirmation before proceeding

### Step 3: Create labels (if they don't exist)

All labels MUST be prefixed with `v{A}::` (version number).

Label format: `v{A}::{category}:{value}`

Use `gh` to create these labels if they don't already exist (version titles: v0 — World and light (Tejas); v1 — Producers (Bindu); v2 — Producer movement; v3 — Nadi and communication; v4 — Consumers (Chara); v5 — Predators (Vyaghra); v6 — Evolution):

```bash
# Version label
gh label create "v0::version:0" --color "0E8A16" --description "Version v0 — World and light (Tejas)" 2>/dev/null || true

# Phase label
gh label create "v0::phase:0.1" --color "5319E7" --description "Phase v0.1 — Skeleton and the Meru tick" 2>/dev/null || true

# Size labels
gh label create "v0::size:S" --color "28A745" --description "Small (1-2 days)" 2>/dev/null || true
gh label create "v0::size:M" --color "FFC107" --description "Medium (3-5 days)" 2>/dev/null || true
gh label create "v0::size:L" --color "DC3545" --description "Large (5-8 days)" 2>/dev/null || true

# Area labels (one per component touched in this phase)
gh label create "v0::area:engine"  --color "6F42C1" 2>/dev/null || true
gh label create "v0::area:species" --color "1D76DB" 2>/dev/null || true
gh label create "v0::area:demos"   --color "0E8A16" 2>/dev/null || true
# ... web / tests as needed
```

### Step 4: Create issues ONE BY ONE

**IMPORTANT:** Issues must be created one at a time, sequentially. After creating each issue:
1. Show the user the result (issue number, URL)
2. Proceed to the next issue immediately (do not wait for confirmation between issues)

For each issue (in order from the summary table):

1. Build the issue body in markdown:

```markdown
## Description
{description from the detailed section}

## What needs to be done
{full content from the detailed section}

## Dependencies
{dependency list, with references to already-created issue numbers}

## Expected result
{expected result from the detailed section}

## Acceptance criteria
{checklist from the detailed section}

---
**ID:** {NADI-xxx}
**Size:** {S/M/L}
**Version:** v{A}
**Phase:** {vA.B from ROADMAP}
**Area:** {engine/species/demos/web/tests}
```

2. Create the issue with a single `gh issue create` command (one issue per command, never batch):

```bash
gh issue create \
  --title "NADI-xxx: {title}" \
  --label "v0::version:0,v0::phase:0.1,v0::size:{S/M/L},v0::area:{area}" \
  --body "$(cat <<'BODY'
{issue body}
BODY
)"
```

3. Record the mapping: NADI-xxx -> GitHub issue #number

4. Report to user: `Created NADI-xxx -> #{number}: {title}`

5. If the issue has dependencies on already-created issues, add a comment (for a dependency from an earlier phase, look up its number in that phase's `vA.B-github-report.md`):

```bash
gh issue comment {issue-number} --body "Blocked by #{dep-issue-number} (NADI-xxx)"
```

6. Move to the next issue.

### Step 5: Generate report

After all issues are created, generate a report file at:
`spec/roadmap/implementation/v{A}.{B}-github-report.md`

Content:

```markdown
# Phase v{A}.{B} -- GitHub Issues Report

**Uploaded:** {date}
**Repository:** {github repo URL}
**Total issues:** {count}

## Issue Mapping

| NADI ID | GitHub # | Title | Phase | Labels | URL |
|---------|----------|-------|-------|--------|-----|
| NADI-001 | #5 | Project skeleton & tooling | v0.1 | v0::version:0, v0::phase:0.1, v0::size:S, v0::area:engine | {url} |
| ... | ... | ... | ... | ... | ... |

## Labels Created

- v{A}::version:{A}
- v{A}::phase:{A.B}
- v{A}::size:S, v{A}::size:M, v{A}::size:L
- v{A}::area:{list}
```

### Step 6: Report to user

Show the user:
- Total issues created
- Link to the GitHub issues page
- Path to the generated report file

## Error Handling

- If `gh` is not authenticated, tell the user to run `gh auth login`
- If the repo has no GitHub remote yet, tell the user to create one (`gh repo create`) before uploading
- If an issue already exists with the same title, skip it and note in the report
- If label creation fails, continue (labels may already exist)
- On any failure, report what was created so far and what remains
