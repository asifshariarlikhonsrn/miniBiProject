# Project plan: SaaS Churn Executive Dashboard

The project is a 3-page Power BI executive dashboard for **Brightlane**, a fictional B2B SaaS company.
It answers one question for the owners: *how much recurring revenue are we losing to churn, from whom, and why?*

The illustrated version of this plan, with the star schema and wireframe diagrams, is in the shared doc:
[SaaS Churn Executive Dashboard — Power BI Build Plan](https://claude.ai/code/artifact/a4155699-185f-475f-9e05-0c7bf8475317).

---

## Phase 1 — Dataset

| Option | Why | Limits | Source |
| --- | --- | --- | --- |
| **A. Brightlane SaaS (generated)**, chosen | Multi-table, 45 months of MRR history, churn reasons, tickets, usage, and deliberate data-quality problems | Synthetic | `scripts/generate_data.py` |
| B. Maven Telecom Customer Churn | 7,043 customers with churn category and reason, public domain | One quarter only, so no time trend | [Maven Data Playground](https://mavenanalytics.io/data-playground/telecom-customer-churn) |
| C. IBM Telco Customer Churn | Well known | Flat, no dates, overused | [Kaggle](https://www.kaggle.com/datasets/blastchar/telco-customer-churn) |

## Phase 2 — Goals and KPIs

The four owner goals:

1. Protect recurring revenue.
2. Find who churns.
3. Explain why they churn.
4. Act early, before accounts leave.

| KPI | Definition | Good direction |
| --- | --- | --- |
| MRR | Active subscription revenue in the month | Up |
| Net New MRR | New + Expansion − Contraction − Churned | Up, above 0 |
| Logo churn rate | Customers lost ÷ customers at the start of the month | Down |
| NRR | (Start + Expansion − Contraction − Churn) ÷ Start MRR | Above 100% |
| At-risk MRR | MRR of accounts with falling usage or 3+ tickets | Down |
| ARR, Gross revenue churn %, Active customers, ARPA, LTV | Supporting KPIs | |

## Phase 3 — Model and Power Query

- **Star schema.** Four facts (`FactSubscriptionMonthly`, `FactChurnEvent`, `FactSupportTicket`, `FactUsage`) and four dimensions (`DimDate`, `DimAccount`, `DimPlan`, `DimChurnReason`). Relationships are one-to-many and single-direction.
- **Queries.** One M script per table is in [`powerquery/`](../powerquery). All of them read from the `DataFolder` parameter.
- **Cleaning.** The fixes are listed in [data-dictionary.md](data-dictionary.md#known-data-quality-issues-fixed-in-power-query).
- **Settings.** Turn off Auto date/time. Mark `DimDate` as the date table. Keep measures in a `_Measures` table, hide the key columns, and save as `.pbip`.

## Phase 4 — DAX

All the measures are in [`dax/measures.dax`](../dax/measures.dax):

- core MRR and its flows
- retention ratios
- time intelligence (MoM, YoY, YTD, a 3-month moving average)
- cohort retention, ranking and at-risk scoring
- the MRR bridge for the waterfall chart
- dynamic titles
- a calculation group and a field parameter

## Phase 5 — Pages and visuals

| Page | Question | Visuals |
| --- | --- | --- |
| 1. Executive Overview | Are we winning? | 5 KPI cards · MRR trend (line and stacked column) · MRR bridge (waterfall) · churned MRR by reason (bar) · top 10 at-risk accounts (table) |
| 2. Churn Drivers | Who leaves, and why? | Cohort retention heatmap (matrix) · churn by plan and region (bars) · decomposition tree · usage vs. tickets (scatter) |
| 3. Customer Detail | What happened to this account? | Drill-through page: profile cards, MRR history, usage line, tickets table |

The theme is in [`report/theme/brightlane-theme.json`](../report/theme/brightlane-theme.json). Use a 1280 × 720 canvas, at most 8 visuals per page and no pie charts.

## Phase 6 — Interactivity

- **Slicers.** A slicer panel synced across pages, opened and closed with bookmarks, with a reset button.
- **Drill-through.** Drill through to Customer Detail on `DimAccount[AccountName]`.
- **Tooltip.** A custom report-page tooltip on the MRR trend.
- **Bookmarks.** A chart/table toggle and a "story mode" bookmark navigator.
- **Extras.** Row-level security by region, a mobile layout, alt text, and a Performance Analyzer check.

## Roadmap

- [ ] Week 1 — Data: run the generator, read the data dictionary
- [ ] Week 2 — Power Query: load and clean all 8 tables, save as `.pbip`
- [ ] Week 3 — Model and core DAX, checking totals against the CSVs
- [ ] Week 4 — Advanced DAX: time intelligence, cohorts, at-risk scoring, calculation group
- [ ] Week 5 — Build pages 1–3, theme, tooltip, drill-through
- [ ] Week 6 — Bookmarks, row-level security, mobile layout, README screenshots, demo video, insights memo
