# SIGNATURE Pipeline — Phase Spec

Design principle: **the machine never waits for a human mid-phase.** Human
judgment is spent at one gate, where it has full context and maximum leverage.

## Phases (fully autonomous, sequential)

Each phase produces a named artifact. A phase may not start until the previous
phase's artifact exists. No approvals between phases.

| # | Phase | Artifact | Definition of done |
|---|---|---|---|
| 1 | Intake parse | `DECISIONS-LOG (draft)` | Every intake field mapped to a decision or an explicit professional default; ambiguities resolved and logged, never asked. |
| 2 | Strategy | Keyword map + sitemap plan | Page list (≤ package limit), primary/secondary keyword per page, conversion path defined. |
| 3 | Identity | Design tokens + logo mark | Color tokens (light+dark, AA-checked), type scale, motion language, SVG mark, OG image. |
| 4 | Copy | All page copy | Unique copy per page (no town-swapping), tagline, blog posts. No fabricated testimonials/stats — ever. |
| 5 | Build | Full static site | Semantic HTML5, single h1, forms + honeypots, scoped JSON-LD, netlify.toml, sitemap/robots. |
| 6 | QA | QA report | Scripted checks (titles/descriptions/canonicals/JSON-LD/links/forms) ALL PASS + real-browser render check in light, dark, and mobile. Failures loop back to Build automatically. |
| 7 | Mockups | Review gallery | Full-page renders of every page packaged into one review document. |

## Gate: Consultant Review (the only stop)

Presented together: DECISIONS LOG · mockup gallery · QA table · file tree.

Consultant responds with one of:
- **APPROVE** → proceed to Delivery.
- **EDITS: <list>** → pipeline applies edits, re-runs QA + affected mockups,
  re-presents. No limit on loops; each loop is autonomous.
- **REJECT PHASE <n>** → pipeline re-runs from that phase with the feedback as
  new constraints.

## Delivery (autonomous, post-approval)

1. Commit + push to the project branch.
2. Update the client status page (`agency/templates/status.html` instance):
   mark completed phases — this is what the client sees.
3. Emit LAUNCH NOTES (domain swap, Netlify connect, GA4, GBP, Search Console).
4. Log support-period end date (launch + 90 days for SIGNATURE).

## Client visibility

Clients never see internal phase churn. Their status page shows five
client-friendly milestones, flipped only at real completion points:

Discovery ✓ → Design ✓ → Build ✓ → Review ✓ → Launch ✓

(Discovery+Design flip after the internal phases 1–3 complete; Build after 5–7;
Review after gate approval; Launch after go-live.)
