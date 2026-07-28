# Next Wave Digital & Consulting — Agency Operating System

This folder is the operating manual for running Next Wave client builds with an
AI production crew and human (consultant) review gates.

> **Note:** this infrastructure currently lives inside a client-site repo because
> it's the only repo connected. Before handing this repo to the client, move
> `agency/` and `.claude/` to a dedicated `nextwave-ops` repo.

## Org chart

| Role | Who | Charter |
|---|---|---|
| CEO / Consultant | Colin | Final review gate on every phase. Approves, edits, or rejects. |
| COO (AI) | `.claude/agents/coo.md` | Operations, quality, efficiency; scans design/brand trends; proposes product improvements; flags risks to CEO. Runs weekly (scheduled). |
| CTO (AI) | `.claude/agents/cto.md` | Tech stack, security, tooling market analysis, education briefs. Runs weekly (scheduled). |
| Production crew (AI) | `/signature-pipeline` skill | Executes client builds end-to-end with no mid-phase approvals. |

## How a client project runs

1. Client fills the intake form (same fields as the SIGNATURE intake).
2. Consultant pastes the intake into a Claude Code session and invokes
   **`/signature-pipeline`**.
3. The pipeline runs **all internal phases sequentially with zero approvals**
   (see `PIPELINE.md`): strategy → identity → copy → build → QA → mockups.
4. It stops at exactly one place: the **Consultant Review Gate**, presenting the
   decisions log, mockup gallery, and QA results.
5. Consultant approves or requests edits (edits loop back through build+QA
   automatically, then re-present).
6. On approval: push, update the client-facing status page
   (`templates/status.html`), and deliver launch notes.

## Weekly executive cadence (scheduled, no intervention needed)

- **Monday — COO Ops Review**: efficiency/quality review of recent work,
  design & branding trend scan, prioritized improvement proposals.
- **Wednesday — CTO Tech Brief**: security check, stack review, tooling market
  table, education summary.

Both run as scheduled Claude sessions; you get a push/email summary when each
completes. Edit cadence or prompts anytime (they're Routines — ask Claude to
list/update triggers). The canonical charters live in `.claude/agents/`; if you
edit a charter meaningfully, ask Claude to sync the Routine prompt to match.

## Figma (free account)

Honest constraints, so we use it where it helps:

- Figma's REST API **cannot author designs** — it's read/comment/export oriented.
  No AI agent (ours or anyone's) can programmatically draw in Figma via API on
  any plan. Design authoring automation requires a plugin running inside the
  Figma desktop/web app.
- **Our leverage:** Next Wave is code-first — the HTML/CSS build *is* the design
  source of truth, and the mockup gallery is generated from it. Use Figma for:
  1. **Client annotation/review** — import rendered pages with the free
     [html.to.design](https://www.figma.com/community/plugin/1159123024924461424)
     plugin (one manual click per import) and let clients comment in Figma.
  2. **Logo/brand asset work** — hand-drawn marks, exported as SVG into `assets/`.
- To let agents *read* Figma files and comments (pull client feedback into the
  pipeline), create a personal access token (Figma → Settings → Security) and
  add `FIGMA_TOKEN` to this Claude environment's variables. The CTO agent's
  charter includes evaluating when a paid Figma tier becomes worth it.

## Files

- `PIPELINE.md` — canonical phase spec with gate definitions
- `templates/status.html` — client-facing project status page template
- `.claude/skills/signature-pipeline/` — the executable pipeline skill
- `.claude/agents/coo.md`, `.claude/agents/cto.md` — executive agent charters
- `reports/` — weekly COO/CTO reports get filed here when run inside a repo session
