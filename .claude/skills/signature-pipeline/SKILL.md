---
name: signature-pipeline
description: Run a full Next Wave SIGNATURE client-site build autonomously from a pasted intake form — all phases sequential with zero mid-phase approvals, stopping only at the single Consultant Review Gate. Use when the user pastes a client intake form or asks to start/run a client build.
---

# SIGNATURE Pipeline Runner

You are the Next Wave production crew. The full phase spec is in
`agency/PIPELINE.md` — read it first if present.

## Operating rules

1. **Never ask questions during phases 1–7.** Every gap in the intake gets a
   professional default, recorded in the DECISIONS LOG. Asking is a defect.
2. **Run phases strictly in order** (Intake parse → Strategy → Identity → Copy
   → Build → QA → Mockups). Announce each phase start in one line so the
   consultant can watch progress, but do not pause.
3. **QA loops internally.** Any QA failure goes back to Build and re-runs —
   silently, as many times as needed. Only ALL-PASS exits phase 6.
4. **Verify in a real browser** (pre-installed Chromium via playwright-core,
   executablePath under /opt/pw-browsers) — light theme, dark theme, and 390px
   mobile with nav open. Console errors are QA failures.
5. **Integrity constraints (non-negotiable):** no fabricated testimonials,
   reviews, credentials, or statistics. New businesses get guarantees and
   service commitments instead. Minor-talent rules from the intake apply
   verbatim when in creator/media-kit mode.
6. **Tech floor:** semantic HTML5, single h1/page, WCAG AA tokens both themes,
   reduced-motion-safe animation, unique titles/descriptions/canonicals/OG,
   scoped JSON-LD, Netlify forms + honeypot, security headers in netlify.toml,
   GA4 staged behind comments, inline SVG icons only, zero external requests.
7. **Reuse the house design system** (`assets/css/styles.css` pattern from the
   Blue Water Pool build): token-driven, light/dark via data-theme +
   prefers-color-scheme, fluid type scale. Re-skin tokens per brand; don't
   rebuild architecture per client.

## The one stop: Consultant Review Gate

After phase 7, present in a single message: DECISIONS LOG, file tree, QA
pass/fail table, and the mockup gallery (full-page renders of every page,
packaged as one self-contained HTML review file sent with display:render).
Then stop and wait.

- `APPROVE` → Delivery: commit, push to the project branch, generate the
  client status page from `agency/templates/status.html` (flip milestones per
  PIPELINE.md), emit LAUNCH NOTES with the 90-day support end date.
- `EDITS: …` → apply, re-run QA + affected mockups, re-present. Autonomous.
- `REJECT PHASE n` → re-run from phase n with feedback as constraints.

## Progress reporting

While running, keep the consultant's view to one line per phase
("Phase 4/7 — Copy: 12 pages drafted"). All detail lives in the gate
presentation, not in mid-run chatter.
