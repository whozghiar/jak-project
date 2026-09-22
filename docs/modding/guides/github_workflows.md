# GitHub Actions Workflows Guide

> - **Applies to:** Jak 1 / Jak 2 / Jak 3 — Modding Infrastructure & CI/CD
> - **Origin:** `master-dev`
> - **Scope:** Automated Upstream Synchronization, Branch Health, Multi-Platform Releases & Issue Triage

## Table of Contents

- [1. CI/CD Architecture & Mental Model](#1-cicd-architecture--mental-model)
- [2. Upstream & Dev Synchronization (`sync-upstream.yaml`)](#2-upstream--dev-synchronization-sync-upstreamyaml)
- [3. Per-Branch Health Check (`branch-sync-check.yaml`)](#3-per-branch-health-check-branch-sync-checkyaml)
  - [Worked example: pushing to a mod branch](#worked-example-pushing-to-a-mod-branch)
- [4. Automated Release & Packaging (`release.yml`)](#4-automated-release--packaging-releaseyml)
- [5. Bug Report Sync (`mod-bug-report-sync.yml`)](#5-bug-report-sync-mod-bug-report-syncyml)
- [6. Bug Triage & Auto-Labeling (`mod-bug-triage.yml`)](#6-bug-triage--auto-labeling-mod-bug-triageyml)
- [7. Master Mod Catalog Sync (`sync-global-catalog.yml`)](#7-master-mod-catalog-sync-sync-global-catalogyml)
- [8. Mod Suggestion Auto-Triage (`mod-suggestion-triage.yml`)](#8-mod-suggestion-auto-triage-mod-suggestion-triageyml)
- [9. Quick Reference Matrix](#9-quick-reference-matrix)

---

## 1. CI/CD Architecture & Mental Model

In this repository, GitHub Actions workflows are engineered to solve two fundamental challenges of OpenGOAL modding:
1. **Parallel Mod Development Without Upstream Divergence:** Retain perfect alignment with official OpenGOAL (`open-goal/jak-project:master`) while simultaneously maintaining 15+ independent mod branches without manual merge overhead.
2. **Player-Grade Distribution:** Deliver fully compiled, statically linked, zero-dependency release archives installable in one click via the official OpenGOAL Launcher.

```text
[Upstream: open-goal/jak-project] (master)
               │
               ▼  (Daily cron at 10:00 UTC: sync-upstream.yaml)
  [origin/master] (Clean Upstream Mirror)
               │
               ▼  (Fast-forward / Merge)
[origin/master-dev] (Modding Core Base: scripts, tools, verified docs)
   │           │
   │           ├── Auto-merge clean branches ──► [origin/jak2/features/my-mod]
   │           │                                         │
   │           │                                         ├── (on: push: branch-sync-check.yaml)
   │           │                                         │     Status Badge: GREEN
   │           │                                         │
   │           │                                         └── Standalone Texture Packs:
   │           │                                             docs/modding/current_mod/texture_packs/*.zip
   │           │                                               │
   │           └── Summary report in GitHub Actions Step Summary│
   │                                                           │
   ▼ (Manual trigger: release.yml) ◄───────────────────────────┘
[GitHub Releases: windows-v*.zip, linux-v*.zip, texture-pack-v*.zip]
   │
   ├── (on: release: mod-bug-report-sync.yml)
   │     Update Mod Concerned dropdown in mod-bug-report.yml
   │
   └── (workflow_call: sync-global-catalog.yml)
         Update root index.json on master-dev (mods + texture packs)
```

---

## 2. Upstream & Dev Synchronization (`sync-upstream.yaml`)

- **File:** [`.github/workflows/sync-upstream.yaml`](../../../.github/workflows/sync-upstream.yaml)
- **When is it called?**
  - **Scheduled Cron:** Daily at `10:00 UTC` (`12:00` Paris summer time).
  - **Manual Trigger:** Any maintainer can trigger it via `workflow_dispatch` from the GitHub Actions tab.
- **Why does it exist?**
  - Prevents our fork from drifting away from upstream bug fixes, compiler enhancements, and engine optimizations.
  - Automates the tedious task of testing and merging `master-dev` into all clean active mod branches (`jak[1-3]/**`).
  - Reports the fleet mergeability summary directly to terminal output and GitHub Actions Step Summary.

### Detailed Execution Trace:
1. **Upstream Fast-Forward:** Fetches `https://github.com/open-goal/jak-project.git:master` and performs a fast-forward merge into our local `master`.
2. **Master-Dev Merge & Workflow Sanitization:** Merges `master` into `master-dev`. Because upstream contains numerous CI workflows that are irrelevant or problematic for mod branches, the step explicitly prunes all workflows except `sync-upstream.yaml`, `release.yml`, `branch-sync-check.yaml`, `mod-bug-report-sync.yml`, and `mod-bug-triage.yml`.
3. **Mod Branch Synchronization:** Runs `python scripts/modding/sync_branches_with_master.py --push`.
   - Tests every active mod branch for mergeability against `origin/master-dev`.
   - If clean (no conflicts), automatically merges `master-dev` and pushes the branch.
   - If conflicts exist, leaves the branch untouched, identifies conflicting files, and generates a concrete resolution command.
   - Generates the summary report in GitHub Actions without polluting the git tree with markdown churn.

---

## 3. Per-Branch Health Check (`branch-sync-check.yaml`)

- **File:** [`.github/workflows/branch-sync-check.yaml`](../../../.github/workflows/branch-sync-check.yaml)
- **When is it called?**
  - **On Push:** Triggered on any push to branches matching `jak[1-3]/**`.
  - **Manual Trigger:** via `workflow_dispatch`.
- **Why does it exist?**
  - GitHub Actions only runs scheduled cron jobs on the **default repository branch** (`master-dev`); it cannot evaluate a separate cron across 15+ mod branches.
  - This workflow provides an ultra-lightweight, 5-second check that powers each mod branch's native GitHub status badge (`?branch=jak2/features/...`).
  - It validates ancestry: `git merge-base --is-ancestor origin/master-dev HEAD`.
  - If a developer pushes commits to a mod branch without syncing with `master-dev` first, the badge immediately turns red, signaling that a sync (`task modding-sync-branch`) is needed.

### Worked example: pushing to a mod branch

1. A developer finishes work on their branch and runs `git push origin jak2/features/my-mod`.
2. The push matches the `jak[1-3]/**` pattern in the workflow's `on: push` trigger, so `branch-sync-check.yaml` runs immediately. The job only needs `contents: read` — it never writes back to the branch.
3. The job checks out the branch with full history (`fetch-depth: 0`), fetches `origin/master-dev`, then runs the actual check:
   ```bash
   git merge-base --is-ancestor origin/master-dev HEAD
   ```
   This asks a single question: does `jak2/features/my-mod` already contain every commit currently on `master-dev`?
4. Two outcomes:
   - **Ancestor check passes:** the step logs a confirmation and the job succeeds. The branch's status badge, embedded in its own `README.md`, renders green:
     ```markdown
     [![Branch Sync Check](https://github.com/whozghiar/jak-project/actions/workflows/branch-sync-check.yaml/badge.svg?branch=jak2%2Ffeatures%2Fmy-mod)](https://github.com/whozghiar/jak-project/actions/workflows/branch-sync-check.yaml?query=branch%3Ajak2%2Ffeatures%2Fmy-mod)
     ```
     (the branch name is URL-encoded in the badge and link — `/` becomes `%2F`).
   - **Ancestor check fails:** the step emits a `::error::` annotation, exits `1`, and the job fails, which turns the badge red. This happens when the developer committed and pushed without first merging the latest `master-dev`. The fix is to run `task modding-sync-branch`.
5. **Caveat:** this workflow only re-runs on a push to the branch. If `master-dev` moves forward afterward and nobody pushes to `jak2/features/my-mod` again, the badge keeps showing its last result (green) — it does not turn red on its own just because `master-dev` advanced. To audit every branch's real mergeability at any time, regardless of recent push activity, run `task modding-branch-status`.

---

## 4. Automated Release & Packaging (`release.yml`)

- **File:** [`.github/workflows/release.yml`](../../../.github/workflows/release.yml)
- **When is it called?**
  - **Manual Trigger Only (`workflow_dispatch`):** Maintainers trigger it from GitHub Actions with required inputs:
    - `mod_name`: Display name (e.g. `Jak 3 JetBoard in Jak 1`).
    - `mod_description`: Short summary included in `index.json`.
    - `tag_name`: Version tag (e.g. `v1.0.0`).
    - `prerelease`: Boolean flag.
- **Why does it exist?**
  - Eliminates "works on my machine" issues by building both **Windows** (Ninja + Clang) and **Linux** executables from clean source in isolated runners.
  - Bakes static libraries (`Release-windows-clang-static`, `Release-linux-clang-static`) so players do not need Visual C++ redistributables or missing shared libraries.
  - Automatically packages the required runtime structure (`gk`, `goalc`, `extractor`, `data/`).
  - **Standalone Texture Pack Packaging:** Automatically scans `docs/modding/current_mod/texture_packs/` for any packaged texture pack `.zip` files, computes their checksums, attaches them as release assets, and registers them under `"texturePacks"` in `index.json`.
  - Computes SHA256 checksums across all assets (`SHA256SUMS.txt`) and updates the mod's `index.json` catalog file, committing it directly back to the branch so the OpenGOAL Launcher immediately detects the update.
  - **Automated Catalog Synchronization:** Automatically invokes `sync-global-catalog.yml` via `workflow_call` at the conclusion of the job, ensuring the unified catalog on `master-dev` is regenerated immediately.

---

## 5. Bug Report Sync (`mod-bug-report-sync.yml`)

- **File:** [`.github/workflows/mod-bug-report-sync.yml`](../../../.github/workflows/mod-bug-report-sync.yml)
- **When is it called?**
  - **On Release:** Triggered whenever a GitHub Release is `published`, `unpublished`, `edited`, or `deleted`.
  - **Manual Trigger:** via `workflow_dispatch`.
- **Why does it exist?**
  - In our GitHub Issue form (`mod-bug-report.yml`), players choose which mod their issue concerns from a dropdown list.
  - A branch may have an `index.json` committed during local testing without having an actual published release.
  - This workflow runs `scripts/modding/sync_bug_report_options.py`, querying the GitHub Releases API to populate the dropdown *strictly* with mods that players can actually download.

---

## 6. Bug Triage & Auto-Labeling (`mod-bug-triage.yml`)

- **File:** [`.github/workflows/mod-bug-triage.yml`](../../../.github/workflows/mod-bug-triage.yml)
- **When is it called?**
  - **On Issue:** Triggered when an issue is `opened` or `edited` with the `mod-bug` label.
- **Why does it exist?**
  - Categorizes bug reports automatically without human maintainer intervention.
  - Uses `actions/github-script` to parse the form fields (`Game`, `Mod Concerned`).
  - Automatically applies labels such as `jak2` and `mod:peaceful-haven-city`.
  - Allows developers to filter open bugs by mod: `is:issue is:open label:mod:<slug>`.
  - When fixing the bug on the mod branch, referencing `Fixes #123` in the commit auto-closes the issue upon merging.

---

## 7. Master Mod Catalog Sync (`sync-global-catalog.yml`)

- **File:** [`.github/workflows/sync-global-catalog.yml`](../../../.github/workflows/sync-global-catalog.yml)
- **When is it called?**
  - **On Release:** Triggered automatically whenever a GitHub Release is `published`, `unpublished`, `edited`, or `deleted`.
  - **Workflow Call:** Called directly at the end of the release pipeline (`release.yml`) to ensure instant catalog updates.
  - **Manual Trigger:** via `workflow_dispatch` on `master-dev`.
- **Why does it exist?**
  - Rather than requiring players to manually find and add 15+ individual mod URLs in their OpenGOAL Launcher, the repository provides a single, consolidated master catalog ([`index.json`](../../../index.json) at the root of `master-dev`).
  - This workflow automates catalog maintenance by running `scripts/modding/sync_global_catalog.py`:
    1. Fetches all releases published across the repository via the GitHub REST API.
    2. Downloads and parses individual release assets and catalogs.
    3. Normalizes branch slugs and dedupes versions.
    4. Aggregates all download URLs (Windows and Linux ZIPs, and standalone texture packs), SHA256 checksums, and cover artwork into a single OpenGOAL Launcher v1 compliant schema.
    5. Commits and pushes the updated `index.json` directly to `master-dev`.

---

## 8. Mod Suggestion Auto-Triage (`mod-suggestion-triage.yml`)

- **File:** [`.github/workflows/mod-suggestion-triage.yml`](../../../.github/workflows/mod-suggestion-triage.yml)
- **When is it called?**
  - **On Issue:** Triggered whenever a community idea or feature suggestion is `opened` or `edited` using the "Mod Suggestion" form (`mod-suggestion.yml`).
- **Why does it exist?**
  - Enables players and developers to suggest new mod ideas directly on the fork.
  - Parses the form's targeted game and category to auto-apply labels:
    - Game labels: `jak1`, `jak2`, `jak3`, `jakx`
    - Category labels: `type:gameplay`, `type:entities`, `type:textures`, `type:audio`, `type:levels`, `type:qol`
    - Status labels: `enhancement`, `mod-suggestion`, `needs-triage`
  - Facilitates community triage and allows mod authors to filter concepts when starting new branches (`task modding-new-branch`).

---

## 9. Quick Reference Matrix

| Workflow | Trigger | Permissions | Target Branch | Primary Outcome |
| :--- | :--- | :--- | :--- | :--- |
| `sync-upstream.yaml` | Schedule (daily 10:00 UTC) / dispatch | `contents: write` | `master`, `master-dev`, all clean `jak*/**` | Mirrors upstream, auto-merges clean branches, updates dashboard. |
| `branch-sync-check.yaml` | Push on `jak[1-3]/**` / dispatch | `contents: read` | Current mod branch | Verifies ancestry with `master-dev`; drives GitHub status badge. |
| `release.yml` | Manual `workflow_dispatch` | `contents: write` | Triggered mod branch | Builds Win/Linux binaries, packages texture packs, creates GitHub Release, updates `index.json`. |
| `sync-global-catalog.yml` | Release events / workflow call / dispatch | `contents: write` | `master-dev` | Consolidates all released mods and texture packs into root `index.json` catalog. |
| `mod-bug-report-sync.yml`| Release events / dispatch | `contents: write` | `master-dev` | Refreshes mod dropdown in bug report issue template. |
| `mod-bug-triage.yml` | Issues (`opened`, `edited`) | `issues: write` | N/A (Repository issues) | Labels bug issues by game (`jak1|2|3`) and mod (`mod:<slug>`). |
| `mod-suggestion-triage.yml` | Issues (`opened`, `edited` with `mod-suggestion`) | `issues: write` | N/A (Repository issues) | Labels mod suggestions by game and category (`type:*`). |
