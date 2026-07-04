# VSM Mapper — Multi-Agent Improvement Plan

## Context

The app (`app/index.html`, ~840 lines, single file, nginx-in-Docker static site) generates Mermaid VSM diagrams from a step form. Evaluation found: (1) the import feature is dead — `parseImportedMermaid` references an undefined `lines` variable in 5 places; (2) the README-advertised live preview / PNG export does not exist in code; (3) time-unit math is naive (regexes the first number, mixes days/hours); (4) no persistence, generic visuals. Goal: fix, then massively improve visually and functionally, split across sub-agents in isolated worktrees each delivering a PR, coordinated by a purpose-built skill.

**Collision reality:** everything lives in one `index.html`. Parallel agents editing it WILL conflict. So Wave 0 is a solo structural refactor that splits the file into modules; only then can agents work in parallel on disjoint files.

## Wave 0 — Foundation (1 agent, solo, blocks everything)

**WS-0: Split the monolith + fix the import bug** — branch `refactor/modularize`
- Split `app/index.html` into:
  - `app/index.html` (markup only)
  - `app/css/styles.css` (current `<style>` block)
  - `app/js/state.js` (step model, localStorage persistence added here: save on change, restore on load)
  - `app/js/generator.js` (`generateMermaidCode`, `escapeHTML`, metrics math)
  - `app/js/parser.js` (`extractMermaidFromMarkdown`, `parseImportedMermaid`)
  - `app/js/ui.js` (DOM wiring, step CRUD, feedback, download)
- Fix the bug: replace the 5 undefined `lines` references in `parseImportedMermaid` (index.html:648, 675, 684, 711, 743) with `filteredLines`.
- Update `app/Dockerfile` to `COPY` the new css/js directories (currently copies only `index.html`).
- Add a tiny JS unit test harness (`tests/unit/`, plain Node `node:test`) covering `generator.js` and `parser.js` round-trip: generate → parse → same steps.
- Verify existing Selenium suite (`tests/test_vsm_generator.py`, 929 lines) still passes headless — behavior must be identical except import now works.
- **PR #1. Merges before any Wave 1 branch is cut.**

## Wave 1 — Parallel feature work (4 agents, disjoint files, branch from post-Wave-0 main)

**WS-1: Live preview + export** — branch `feat/live-preview` — owns `app/js/preview.js`, a `<div id="previewPane">` region in index.html, `app/vendor/mermaid.min.js`
- Vendor mermaid.js locally (no CDN; keeps "zero dependency / offline" claim true).
- Two-pane layout hook: render diagram into preview pane, debounced (300 ms) on any form change — no Generate-button gating (button stays, now just reveals the code block).
- Zoom controls (25–400%, +/-/0 keys), fullscreen toggle, pan by drag.
- PNG and SVG export from the rendered diagram (canvas serialization for PNG).
- Selenium tests: preview renders an `svg`, updates on edit, export downloads a file.

**WS-2: Correct time model + %C&A metrics** — branch `feat/time-units` — owns `app/js/time.js`, edits `generator.js` + the step-input template in `ui.js`
- Replace free-text time inputs with number + unit `<select>` (min/hr/day/wk); normalize to minutes in `time.js`.
- Backward compat: parser maps legacy strings ("2 days") into the structured model.
- Add optional %C&A input per step; compute rolled first-pass yield; metrics subgraph shows PT/LT/FE in a human unit ("3.2 days") instead of "units".
- Unit tests for every conversion + FE math; update the Selenium golden output (`EXPECTED_MERMAID_OUTPUT` in test_vsm_generator.py).

**WS-3: Bottleneck analysis + drag reorder** — branch `feat/bottlenecks` — owns `app/js/analysis.js`, edits `generator.js` (edge styling only) + `ui.js` (drag handles)
- Auto-style the top-N longest waits: red/thick dashed `linkStyle` lines in generated Mermaid.
- Horizontal timeline bar under the metrics (per-step PT vs wait segments, proportional widths) rendered as inline SVG — makes the constraint visually obvious.
- Drag-to-reorder steps (native HTML5 drag & drop on `.input-group`), replacing reliance on insert-before.
- Tests: reorder via Selenium ActionChains; linkStyle present for max wait.

**WS-4: Visual overhaul** — branch `feat/visual-refresh` — owns `app/css/*` only (hard rule: no JS edits; may add classes/data-attrs to index.html markup)
- Two-pane responsive layout (form left, preview right; stacks on mobile), sticky metrics header with PT/LT/FE stat tiles.
- Coherent palette + dark mode (`prefers-color-scheme` + toggle), higher-contrast role colors (swap the pastel `predefinedColors` list — coordinate: this one value lives in generator.js, so WS-4 files an issue and WS-2's owner or the coordinator applies it).
- Drop the Tailwind CDN: replace used utility classes with the hand-rolled stylesheet.
- Visual regression: Selenium screenshots at 3 viewports checked into `tests/screenshots/`.

**Conflict matrix:** WS-1/2/3 all touch `generator.js` and `ui.js` lightly. Mitigation: each workstream's edits are confined to declared functions (WS-1: none in generator; WS-2: metrics block; WS-3: linkStyle append) and PRs merge in order WS-2 → WS-3 → WS-1, rebasing between merges. WS-4 is CSS/markup-only and merges last.

## Wave 2 — VSM methodology features (2 agents, after Wave 1 merges)

**WS-5: Current vs. Future state** — branch `feat/state-compare` — owns `app/js/versions.js`
- Named map versions stored in localStorage; toggle/side-by-side compare; delta readout ("Lead time 34d → 12d, FE 8% → 31%").

**WS-6: Flow roadmap + dependencies** — branch `feat/flow-roadmap` — owns `app/js/roadmap.js`
- Per-step dependency annotations (external team/system) rendered as annotated nodes; a roadmap panel listing improvement actions tied to specific waits with projected lead-time savings, exportable in the Markdown doc.

## Wave 3 — Docs & release (1 agent)

**WS-7:** README rewrite to match reality, changelog, bump `APP_VERSION`, rebuild/verify Docker image, full Selenium + unit suite green.

## Every workstream's Definition of Done
1. Own worktree (`EnterWorktree` / `git worktree add`), own branch, no edits outside declared file ownership.
2. Unit tests (where logic) + Selenium coverage for the feature; full existing suite passes headless (`tests/run_tests.py`).
3. Docs updated (`changelog.md` entry; feature doc in `docs/` if user-facing).
4. Verified live: `scripts/deploy.sh` (or `python -m http.server` in `app/`) + manual/driver check.
5. PR opened with test evidence; coordinator merges in the declared order.

## Coordinator skill prompt (deliverable — paste into the Anthropic skill-creator)

```
Create a skill named "vsm-fleet-coordinator".

Purpose: Orchestrate a multi-agent improvement program for the vsm-mapper repo
(a single-page Mermaid VSM generator served by nginx/Docker). The skill manages
sub-agents working in isolated git worktrees, each owning one workstream and
delivering one PR, merged in a strict dependency order.

When invoked, the skill must:

1. READ the program plan at .claude/plans/vsm-improvement-plan.md (workstreams
   WS-0..WS-7, waves 0-3, file-ownership map, merge order). Treat file ownership
   as a hard contract.

2. WAVE GATING: Never start a wave until every PR in the prior wave is merged to
   main and the full test suite (tests/run_tests.py headless + tests/unit/) is
   green on main. Wave 0 (WS-0 refactor/modularize) is always solo.

3. For each workstream in the current wave, spawn one sub-agent with
   isolation: worktree and a prompt containing: (a) the workstream's spec copied
   verbatim from the plan, (b) its branch name, (c) the exact list of files it
   may create/modify — instruct it to stop and report rather than touch any
   other file, (d) the Definition of Done: unit + Selenium tests written and
   passing, full existing suite green, changelog.md entry, feature verified in
   a running instance, PR opened via `gh pr create` with test output pasted in
   the body.

4. MERGE SEQUENCING within a wave: merge PRs in the plan's declared order
   (Wave 1: WS-2, WS-3, WS-1, WS-4). After each merge, instruct the next
   workstream's agent (via SendMessage) to rebase onto main and re-run the full
   suite before its PR is merged.

5. CONFLICT PROTOCOL: If an agent reports it needs a file it doesn't own,
   do not let it edit; either (a) apply the change yourself on main as a tiny
   coordination commit both branches rebase onto, or (b) re-scope ownership in
   the plan file and record why.

6. VERIFICATION: After each merge, run the Selenium suite headless and boot the
   app (python3 -m http.server in app/ or scripts/deploy.sh) to smoke-test the
   merged feature yourself. A red suite reverts the merge and returns the work
   to its agent with the failure output.

7. STATUS: Maintain .claude/plans/vsm-fleet-status.md — a table of workstream,
   agent, branch, state (pending/in-progress/PR-open/merged/blocked), and
   blockers. Update it on every state change. Report a summary to the user at
   each wave boundary and stop for user approval before starting the next wave.

8. NEVER force-push, never merge with a red suite, never let two agents hold
   write claims on the same file.
```

## Verification (program level)
- After Wave 0: import round-trip works in the browser (paste generated code → Parse and Load → identical form); Selenium suite green; Docker image builds and serves.
- After each wave: full suite green on main, app smoke-tested via deployed container.
- Final: README claims all demonstrably true; fresh `docker run` matches docs.
