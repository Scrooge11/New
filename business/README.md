# Business plan, marketing strategy and financial model

The client-ready business plan (executive summary, market and competitive analysis, marketing strategy, website and Google SEO plan, operations, team, three-year financials, funding, risks, 90-day launch plan, appendices) is a shared document:

https://claude.ai/code/artifact/13d0c254-1267-4cf4-9e7a-a4d02fb08294

It can be edited inline, commented on, shared, and exported to Word or PDF from the document's menu.

## In this folder

| File | What it is |
|---|---|
| `js-financial-model.xlsx` | Three-year financial model. Sheets: Assumptions (yellow cells are the levers), Startup Costs, Annual Summary, Monthly (36 months of P&L and cash flow). Every number outside the blue input cells is a formula; open it in Excel or Google Sheets and it recalculates. |
| `build_model.py` | The script that generates the workbook (openpyxl). Edit and rerun to change the structure. |
| `research/industry-market.md` | Industry size, EV and heat-pump demand, housing stock, town profiles, pricing benchmarks, labor, Massachusetts regulation, seasonality, with sources. |
| `research/competitors.md` | 15 local electrical contractors, how they market, pricing signals, and the gap analysis behind the positioning. |
| `research/seo-marketing.md` | Keyword research, what the Google results page looks like locally, Business Profile practice, paid-channel costs, review statistics, technical SEO, budget benchmarks. |
| `research/costs-operations.md` | Startup cost line items, insurance, software, operating benchmarks, revenue benchmarks, financing options, pricing models. |

## Assumptions to confirm with the owner

The plan and the website assume a Westford, MA home base and the towns within about 30 miles (northern Middlesex County). Month 1 of the model is the first month of operations; the launch date is not set. Research figures were read from search listings in October 2026 because this environment could not open the source pages; verify any figure before it goes to a lender.

## Verification note

LibreOffice's Calc component is not installed in the build environment, so the workbook was evaluated with the Python `formulas` engine instead: 2,860 cells, zero formula errors. The figures quoted in the plan come from that evaluation.
