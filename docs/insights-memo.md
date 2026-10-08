# Insights memo: Brightlane churn review

**To:** Brightlane owners · **Period:** Oct 2024 – Sep 2026 · **Source:** Brightlane SaaS Churn Dashboard

> Brightlane is a fictional company and all data is synthetic. This memo shows how the dashboard turns data into decisions.

## Bottom line

MRR grew to **$3.81M** (+2.9% in September), but growth is coming from new sign-ups, not from keeping customers.
Net revenue retention over the last 12 months is **85.7%**, well below the 100% that self-sustaining SaaS businesses aim for.
**$485K of MRR (12.7%) sits in 217 accounts showing warning signs right now.**

## Findings

1. **Support is the biggest single cause of lost revenue.**
   - "Poor support experience" accounts for **23% of churned MRR** ($182K over 24 months), more than any other reason.
   - In Jan–Mar 2026, average ticket resolution time **more than doubled, from 8.4 to 19.3 hours**.
   - Monthly churn rose to 3.3–3.9% in those months, then fell back once resolution times recovered.
2. **The July 2025 Basic price rise backfired.**
   - Basic went from $15 to $19 per seat, and Basic churn jumped from about 3% to **7.8% in July 2025**.
   - It stayed high through September 2025.
   - "Price too high" is the second-largest reason for lost MRR (14.5%).
3. **Churn is concentrated in small plans.**
   - Average monthly logo churn is **3.7% on Basic**, 2.1% on Pro and 0.8% on Enterprise.
4. **Acquisition channel predicts retention.**
   - Paid Ads customers churn at **2.9% a month**, against 2.1% for Partner-referred customers.
   - APAC is the weakest region at 3.0%, against 2.3% for EMEA.
5. **We don't know why 12% of lost MRR left.**
   - Those churn events have no reason recorded, which weakens every analysis above.

## Recommendations

| # | Action | Expected impact | Owner |
| --- | --- | --- | --- |
| 1 | Set a support SLA (for example, high-priority tickets under 8 hours) and staff ahead of peaks. Alert when resolution time rises 50% month on month | Protects the largest churn reason (23% of lost MRR) | Head of Support |
| 2 | Work the **Top 10 at-risk accounts** list every week, then the full 217. Customer success calls start with the largest MRR | Up to $485K of MRR at stake | Customer Success |
| 3 | For future price changes, grandfather existing Basic customers for 6 months and offer an annual-plan discount | Avoids a repeat of the 7.8% churn spike | Pricing / Finance |
| 4 | Shift acquisition budget from Paid Ads toward the Partner channel | About 0.8 pts lower monthly churn on new cohorts | Marketing |
| 5 | Make churn reason a required field in the cancellation flow | Closes the 12% blind spot | Product |

## How to use the dashboard

- **Executive Overview:** check the five KPI cards each month. Green or red sub-lines show the direction against last month.
- **Churn Drivers:** use the decomposition tree to find where lost MRR comes from (reason → plan → region).
- **Customer Detail:** right-click any account to see its MRR history, usage trend and support tickets before a call.
