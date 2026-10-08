# Data dictionary

Brightlane is a **fictional** B2B SaaS company. The data is synthetic, produced by
`scripts/generate_data.py` (seed 42, so every run gives the same files). It covers
**Jan 2023 – Sep 2026** (45 months).

| File | Rows | Grain | Becomes |
| --- | --- | --- | --- |
| `accounts.csv` | 2,926 (2,879 unique accounts) | account | `DimAccount` |
| `plans.csv` | 3 | plan | `DimPlan` |
| `churn_reasons.csv` | 8 | reason | `DimChurnReason` (+ "Not stated") |
| `subscriptions_monthly.csv` | 42,575 | account × month | `FactSubscriptionMonthly` |
| `churn_events.csv` | 992 | churned account | `FactChurnEvent` |
| `support_tickets.csv` | 32,857 | ticket | `FactSupportTicket` |
| `usage_monthly.csv` | 41,583 | account × month | `FactUsage` |

## Columns

**accounts.csv**: `account_id`, `account_name`, `industry`, `region`, `company_size`, `acquisition_channel`, `signup_date`

**plans.csv**: `plan_id` (1 Basic, 2 Pro, 3 Enterprise), `plan_name`, `price_per_seat` (current list price)

**churn_reasons.csv**: `reason_code`, `reason`, `reason_group` (Price / Product / Service / Competitor / Other)

**subscriptions_monthly.csv**
- `month_start`: the first day of the month
- `mrr`: monthly recurring revenue at the end of the month, which is 0 in the churn month
- `mrr_change`: `mrr` minus the previous month's `mrr`
- `movement_type`: New, Expansion, Contraction, Churn or Flat

MRR always reconciles: last month's MRR + the sum of `mrr_change` = this month's MRR.

**churn_events.csv**: `account_id`, `plan_id` (plan at churn), `churn_date`, `reason_code`, `mrr_lost` (the MRR in the month before churn)

**support_tickets.csv**: `ticket_id`, `account_id`, `created_date`, `priority`, `category`, `resolution_hours`, `csat` (1–5). Open tickets have no resolution hours or CSAT.

**usage_monthly.csv**: `account_id`, `month_start`, `active_users`, `logins`

## Known data-quality issues (fixed in Power Query)

| File | Issue | Count | Fix (`powerquery/`) |
| --- | --- | --- | --- |
| accounts | Duplicate account rows | 47 | `Table.Distinct` on `account_id` |
| accounts | Region spelled 12 ways ("NA", "N. America", "north america ", "Europe", "apac "…) | 1,546 rows not in standard form | Trim, upper-case, map with a lookup record |
| accounts | `signup_date` in `dd/MM/yyyy` instead of ISO | 141 | Custom `ParseDate` function |
| accounts | Industry in lower case | 181 | `Text.Proper` |
| accounts | Trailing spaces in `account_name` | 126 | `Text.Trim` |
| accounts | Blank `company_size` | 123 | Replace with "Unknown" |
| churn_events | Blank `reason_code` | 102 of 992 | Replace with "NS" (Not stated) |
| support_tickets | `priority` casing and leading spaces ("HIGH", " Medium") | 2,303 | `Text.Proper(Text.Trim())` |
| support_tickets | Open tickets: blank `resolution_hours` / `csat` | 1,201 | Kept as null, flagged with `IsOpen` |

## Stories in the data (for the insights memo)

- **The July 2025 Basic price rise** (from $15 to $19 per seat) pushed Basic churn from about 3% to 7.8% in Jul 2025. Churn stayed high through September, and most of these accounts cite "Price too high".
- **The Jan–Mar 2026 support backlog** made tickets take longer to resolve. Churn rose to 3–4% a month, mostly among accounts with several recent tickets, and "Poor support experience" became a top reason.
- **Health signals lead churn.** Accounts with falling active users and rising ticket counts churn far more often. This is the basis for the At-Risk MRR measure.
- Enterprise accounts churn least. Paid Ads sign-ups and APAC accounts churn most.
