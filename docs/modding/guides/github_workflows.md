# GitHub Actions Workflows Guide

> - **Applies to:** Jak 1 / Jak 2 / Jak 3 — Modding Infrastructure & CI/CD
> - **Origin:** `master-dev`
> - **Scope:** Automated Upstream Synchronization, Branch Health, Lint/Build Checks, Multi-Platform Releases & Issue Triage

## Table of Contents

- [1. CI/CD Architecture & Mental Model](#1-cicd-architecture--mental-model)
- [2. Upstream & Dev Synchronization (`sync-upstream.yaml`)](#2-upstream--dev-synchronization-sync-upstreamyaml)
- [3. On-Demand Branch Sync (`sync-branch-with-master-dev.yml`)](#3-on-demand-branch-sync-sync-branch-with-master-devyml)
- [4. Per-Branch Health Check (`branch-sync-check.yaml`)](#4-per-branch-health-check-branch-sync-checkyaml)
  - [Worked example: pushing to a mod branch](#worked-example-pushing-to-a-mod-branch)
- [5. Source Lint (`lint.yml`)](#5-source-lint-lintyml)
- [6. Build Check (`build.yml`)](#6-build-check-buildyml)
- [7. Automated Release & Packaging (`release.yml`)](#7-automated-release--packaging-releaseyml)
- [8. Bug Report Sync (`mod-bug-report-sync.yml`)](#8-bug-report-sync-mod-bug-report-syncyml)
- [9. Bug Triage & Auto-Labeling (`mod-bug-triage.yml`)](#9-bug-triage--auto-labeling-mod-bug-triageyml)
- [10. Mod Suggestion Auto-Triage (`mod-suggestion-triage.yml`)](#10-mod-suggestion-auto-triage-mod-suggestion-triageyml)
- [11. Master Mod Catalog Sync (`sync-global-catalog.yml`)](#11-master-mod-catalog-sync-sync-global-catalogyml)
- [12. Quick Reference Matrix](#12-quick-reference-matrix)

---

## 1. CI/CD Architecture & Mental Model

In this repository, GitHub Actions workflows are engineered to solve three fundamental challenges of OpenGOAL modding:
1. **Parallel Mod Development Without Upstream Divergence:** Retain perfect alignment with official OpenGOAL (`open-goal/jak-project:master`) while simultaneously maintaining 15+ independent mod branches, each caught up with `master-dev` on demand rather than by surprise.
2. **Player-Grade Distribution:** Deliver fully compiled, statically linked, zero-dependency release archives installable in one click via the official OpenGOAL Launcher.
3. **Fast, Low-Noise Feedback On Every Branch:** Catch broken syntax and non-compiling code on any mod branch, on demand or on every push, without running the full release pipeline for it.

```text
[Upstream: open-goal/jak-project] (master)
               │
               ▼  (Daily cron at 10:00 UTC: sync-upstream.yaml)
  [origin/master] (Clean Upstream Mirror)
               │
               ▼  (Fast-forward / Merge)
[origin/master-dev] (Modding Core Base: scripts, tools, verified docs)
               │
               ▼  (Manual, per branch: sync-branch-with-master-dev.yml)
[origin/jak2/features/my-mod]
   │
   ├── (on: push: branch-sync-check.yaml)
   │     Status Badge: GREEN
   │
   ├── (on: push: lint.yml)
   │     Fast source checks
   │
   ├── Standalone Texture Packs:
   │     docs/modding/current_mod/texture_packs/*.zip
   │
   ▼ (Manual trigger: release.yml)
[GitHub Releases: windows-v*.zip, linux-v*.zip, texture-pack-v*.zip]
   │
   ├── (on: release: mod-bug-report-sync.yml)
   │     Update Mod Concerned dropdown in mod-bug-report.yml
   │
   └── (gh workflow run: sync-global-catalog.yml)
         Update root index.json on master-dev (mods + texture packs)
```

`sync-upstream.yaml` stops at `master-dev` — it never touches mod branches. Catching up `origin/jak2/features/my-mod` (or any other mod branch) with `master-dev` is always a deliberate action: `sync-branch-with-master-dev.yml` for one branch from the Actions tab, or `task modding-branch-status -- --push` locally for every clean branch in one pass. `build.yml` (manual compile check) is the other on-demand tool that sits outside this pipeline, usable from any branch that carries the file.

---

## 2. Upstream & Dev Synchronization (`sync-upstream.yaml`)

- **File:** [`.github/workflows/sync-upstream.yaml`](../../../.github/workflows/sync-upstream.yaml)
- **When is it called?**
  - **Scheduled Cron:** Daily at `10:00 UTC` (`12:00` Paris summer time).
  - **Manual Trigger:** Any maintainer can trigger it via `workflow_dispatch` from the GitHub Actions tab.
- **Why does it exist?**
  - Prevents our fork from drifting away from upstream bug fixes, compiler enhancements, and engine optimizations.
  - Keeps `master-dev` (the base every mod branch is created from and synced against) current with `master`, without ever touching a mod branch directly.
- **Scope, deliberately:** this workflow stops at `master-dev`. It used to also auto-merge every clean mod branch once a day; that step was removed so a mod branch only ever changes when someone deliberately syncs it (§3) — no surprise commits landing on a branch overnight.

### Detailed Execution Trace:
1. **Upstream Fast-Forward:** Fetches `https://github.com/open-goal/jak-project.git:master` and performs a fast-forward merge into our local `master`.
2. **Master-Dev Merge & Workflow Sanitization:** Merges `master` into `master-dev`. Because upstream contains numerous CI workflows that are irrelevant or problematic for mod branches, the step explicitly prunes all workflows except the ones listed in its own `allowed_workflows` array (kept in sync with `scripts/modding/sync_common.ALLOWED_MOD_BRANCH_WORKFLOWS` plus the repo-wide, master-dev-only automation: `sync-upstream.yaml`, `release.yml`, `branch-sync-check.yaml`, `lint.yml`, `build.yml`, `sync-branch-with-master-dev.yml`, `sync-global-catalog.yml`, `mod-bug-report-sync.yml`, `mod-bug-triage.yml`, `mod-suggestion-triage.yml`).

To catch mod branches up with the newly-updated `master-dev`, see §3 (one branch, on demand) or run `task modding-branch-status -- --push` locally (every clean branch, in one pass — the same `scripts/modding/sync_branches_with_master.py` this workflow used to call automatically).

---

## 3. On-Demand Branch Sync (`sync-branch-with-master-dev.yml`)

- **File:** [`.github/workflows/sync-branch-with-master-dev.yml`](../../../.github/workflows/sync-branch-with-master-dev.yml)
- **When is it called?**
  - **Manual Trigger Only (`workflow_dispatch`):** Pick the branch to sync with "Use workflow from" in the Actions tab, then run it. No inputs required — the selected branch is the one that gets synced.
- **Why does it exist?**
  - `sync-upstream.yaml` (§2) no longer touches mod branches automatically — this is the primary, day-to-day way a mod branch actually gets `master-dev`'s changes, straight from the Actions tab, without needing a local checkout.
  - This is the GitHub UI equivalent of running `task modding-sync-branch -- --push` locally: it wraps `scripts/modding/sync_branch_with_master_dev.py --push`, which resolves the same deterministic README/doc/workflow conflicts the fleet-wide script resolves (see `scripts/modding/sync_common.py`), then pushes.
  - **Merge only, never rebase.** A CI-triggered rebase would force-push over a branch's published history with nobody there to review the result first. Do that locally instead (`task modding-sync-branch -- --rebase`) if a linear history is actually needed.
  - Refuses to run against `master` or `master-dev` (there is nothing to sync them with — they *are* the source).

---

## 4. Per-Branch Health Check (`branch-sync-check.yaml`)

- **File:** [`.github/workflows/branch-sync-check.yaml`](../../../.github/workflows/branch-sync-check.yaml)
- **When is it called?**
  - **On Push:** Triggered on any push to branches matching `jak[1-3]/**`.
  - **Manual Trigger:** via `workflow_dispatch`.
- **Why does it exist?**
  - GitHub Actions only runs scheduled cron jobs on the **default repository branch** (`master-dev`); it cannot evaluate a separate cron across 15+ mod branches.
  - This workflow provides an ultra-lightweight, 5-second check that powers each mod branch's native GitHub status badge (`?branch=jak2/features/...`).
  - It validates ancestry: `git merge-base --is-ancestor origin/master-dev HEAD`.
  - If a developer pushes commits to a mod branch without syncing with `master-dev` first, the badge immediately turns red, signaling that a sync (`task modding-sync-branch`, or the `sync-branch-with-master-dev.yml` workflow) is needed.

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
   - **Ancestor check fails:** the step emits a `::error::` annotation, exits `1`, and the job fails, which turns the badge red. This happens when the developer committed and pushed without first merging the latest `master-dev`. The fix is to run `task modding-sync-branch`, or run the `sync-branch-with-master-dev.yml` workflow against that branch.
5. **Caveat:** this workflow only re-runs on a push to the branch. If `master-dev` moves forward afterward and nobody pushes to `jak2/features/my-mod` again, the badge keeps showing its last result (green) — it does not turn red on its own just because `master-dev` advanced. To audit every branch's real mergeability at any time, regardless of recent push activity, run `task modding-branch-status`.

---

## 5. Source Lint (`lint.yml`)

- **File:** [`.github/workflows/lint.yml`](../../../.github/workflows/lint.yml)
- **When is it called?**
  - **On Push:** Every push, on every branch (this file is synced onto every mod branch, see `scripts/modding/sync_common.ALLOWED_MOD_BRANCH_WORKFLOWS`).
  - **Manual Trigger:** via `workflow_dispatch`.
- **Why does it exist?**
  - Every check it runs finishes in seconds and needs no build — cheap enough to run on every single push without burning meaningful CI time.
  - Runs `scripts/ci/lint-trailing-whitespace.py` (no trailing whitespace in `goal_src`), `scripts/ci/check-for-asserts.py` (no raw `assert()` in the C++ engine), `scripts/ci/lint-autoglottonyms.py` and `scripts/ci/lint-characters.py` (translation files stay within each game's allowed character set and never retranslate a language's own name), and `scripts/ci/lint-gsrc-removals.py` (fails if a diff against `origin/master` removes a line tagged `og:preserve-this` from `goal_src`).
  - Read-only (`contents: read`) — it only reports, it never auto-fixes or commits anything.

---

## 6. Build Check (`build.yml`)

- **File:** [`.github/workflows/build.yml`](../../../.github/workflows/build.yml)
- **When is it called?**
  - **Manual Trigger Only (`workflow_dispatch`):** Pick any branch that carries this file with "Use workflow from" in the Actions tab, then run it.
- **Why does it exist?**
  - Answers exactly one question — "does this branch still compile?" — for `gk`, `goalc`, and `extractor` on Windows (Clang-CL static) and Linux (Clang static), the same targets and presets `release.yml` builds.
  - No packaging, no `index.json` update, no GitHub Release: it only uploads the raw binaries as short-lived (3-day) build artifacts so a maintainer can grab and sanity-check them.
  - Kept manual rather than on every push on purpose: a full Release-config Windows+Linux build takes roughly 30-60 minutes, and this fork has 15+ active mod branches — running it automatically on every push across all of them would burn far more CI time than the check is worth. Run it before cutting a release, or whenever there is a reason to doubt a branch still builds.

---

## 7. Automated Release & Packaging (`release.yml`)

- **File:** [`.github/workflows/release.yml`](../../../.github/workflows/release.yml)
- **When is it called?**
  - **Manual Trigger Only (`workflow_dispatch`):** Maintainers trigger it from GitHub Actions with required inputs:
    - `mod_name`: Display name (e.g. `Jak 3 JetBoard in Jak 1`).
    - `mod_description`: Short summary included in `index.json`.
    - `tag_name`: Version tag (e.g. `v1.0.0`).
    - `prerelease`: Boolean flag.
  - **Usable from any branch:** there is no `branches:` restriction on `workflow_dispatch` — pick any branch that carries this file (every mod branch does) with "Use workflow from" and run it directly, no need to be on `master`/`master-dev` first.
- **Why does it exist?**
  - Eliminates "works on my machine" issues by building both **Windows** (Ninja + Clang) and **Linux** executables from clean source in isolated runners.
  - Bakes static libraries (`Release-windows-clang-static`, `Release-linux-clang-static`) so players do not need Visual C++ redistributables or missing shared libraries.
  - Automatically packages the required runtime structure (`gk`, `goalc`, `extractor`, `data/`).
  - **Standalone Texture Pack Packaging:** Automatically scans `docs/modding/current_mod/texture_packs/` for any packaged texture pack `.zip` files, computes their checksums, attaches them as release assets, and registers them under `"texturePacks"` in `index.json`.
  - Computes SHA256 checksums across all assets (`SHA256SUMS.txt`) and updates the mod's `index.json` catalog file, committing it directly back to the branch so the OpenGOAL Launcher immediately detects the update.
  - **Automated Catalog Synchronization:** Automatically invokes `sync-global-catalog.yml` via `workflow_call` at the conclusion of the job, ensuring the unified catalog on `master-dev` is regenerated immediately.

---

## 8. Bug Report Sync (`mod-bug-report-sync.yml`)

*Part of the **Bugs Actions** group — GitHub Actions has no native folder/section grouping in the Actions tab, so this workflow, `mod-bug-triage.yml`, and `mod-suggestion-triage.yml` share a `Bugs:` name prefix to cluster together in the (alphabetically sorted) workflow list.*

- **File:** [`.github/workflows/mod-bug-report-sync.yml`](../../../.github/workflows/mod-bug-report-sync.yml)
- **When is it called?**
  - **On Release:** Triggered whenever a GitHub Release is `published`, `unpublished`, `edited`, or `deleted`.
  - **Manual Trigger:** via `workflow_dispatch`.
- **Why does it exist?**
  - In our GitHub Issue form (`mod-bug-report.yml`), players choose which mod their issue concerns from a dropdown list.
  - A branch may have an `index.json` committed during local testing without having an actual published release.
  - This workflow runs `scripts/modding/sync_bug_report_options.py`, querying the GitHub Releases API to populate the dropdown *strictly* with mods that players can actually download.

---

## 9. Bug Triage & Auto-Labeling (`mod-bug-triage.yml`)

*Part of the **Bugs Actions** group — see the note under §8.*

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

## 10. Mod Suggestion Auto-Triage (`mod-suggestion-triage.yml`)

*Part of the **Bugs Actions** group — see the note under §8.*

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

## 11. Master Mod Catalog Sync (`sync-global-catalog.yml`)

*Part of the **Catalog Mods** group — this workflow shares a `Catalog:` name prefix so it stands out in the Actions tab's workflow list; see the grouping note under §8.*

- **File:** [`.github/workflows/sync-global-catalog.yml`](../../../.github/workflows/sync-global-catalog.yml)
- **When is it called?**
  - **On Release:** Triggered automatically whenever a GitHub Release is `published`, `unpublished`, `edited`, or `deleted`.
  - **Workflow Call:** Called directly at the end of the release pipeline (`release.yml`) to ensure instant catalog updates.
  - **Manual Trigger:** via `workflow_dispatch`.
- **Why does it exist?**
  - Rather than requiring players to manually find and add 15+ individual mod URLs in their OpenGOAL Launcher, the repository provides a single, consolidated master catalog ([`index.json`](../../../index.json) at the root of `master-dev`).
  - **Master-dev only, regardless of trigger branch:** every job step explicitly checks out `ref: master-dev` and pushes back to `master-dev` — running it from a release cut on a mod branch never touches that branch's own `index.json`, only the global one.
  - This workflow automates catalog maintenance by running `scripts/modding/sync_global_catalog.py`:
    1. Fetches all releases published across the repository via the GitHub REST API.
    2. Downloads and parses individual release assets and catalogs.
    3. Normalizes branch slugs and dedupes versions.
    4. Aggregates all download URLs (Windows and Linux ZIPs, and standalone texture packs), SHA256 checksums, and cover artwork into a single OpenGOAL Launcher v1 compliant schema.
    5. Commits and pushes the updated `index.json` directly to `master-dev`.

---

## 12. Quick Reference Matrix

| Workflow | Trigger | Permissions | Target Branch | Primary Outcome |
| :--- | :--- | :--- | :--- | :--- |
| `sync-upstream.yaml` | Schedule (daily 10:00 UTC) / dispatch | `contents: write` | `master`, `master-dev` only | Fast-forwards `master` from upstream, merges it into `master-dev`. Never touches mod branches. |
| `sync-branch-with-master-dev.yml` | Manual `workflow_dispatch` | `contents: write` | Any branch except `master`/`master-dev` | On-demand merge of `master-dev` into the selected branch, then push. |
| `branch-sync-check.yaml` | Push on `jak[1-3]/**` / dispatch | `contents: read` | Current mod branch | Verifies ancestry with `master-dev`; drives GitHub status badge. |
| `lint.yml` | Push (any branch) / dispatch | `contents: read` | Any branch | Fast source checks: whitespace, forbidden `assert()`, translation chars/autoglottonyms, preserved `goal_src` markers. |
| `build.yml` | Manual `workflow_dispatch` | `contents: read` | Any branch that carries the file | Compiles `gk`/`goalc`/`extractor` for Windows+Linux Release as a pure compile check; uploads binaries as build artifacts. |
| `release.yml` | Manual `workflow_dispatch` | `contents: write` | Any branch that carries the file | Builds Win/Linux binaries, packages texture packs, creates GitHub Release, updates `index.json`. |
| `mod-bug-report-sync.yml`| Release events / dispatch | `contents: write` | `master-dev` | Refreshes mod dropdown in bug report issue template. |
| `mod-bug-triage.yml` | Issues (`opened`, `edited`) | `issues: write` | N/A (Repository issues) | Labels bug issues by game (`jak1|2|3`) and mod (`mod:<slug>`). |
| `mod-suggestion-triage.yml` | Issues (`opened`, `edited` with `mod-suggestion`) | `issues: write` | N/A (Repository issues) | Labels mod suggestions by game and category (`type:*`). |
| `sync-global-catalog.yml` | Release events / workflow call / dispatch | `contents: write` | `master-dev` | Consolidates all released mods and texture packs into root `index.json` catalog. |
