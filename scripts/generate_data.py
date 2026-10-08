"""Generate the Brightlane (fictional) B2B SaaS churn dataset.

Writes 7 CSV files to data/raw/. Uses only the Python standard library and a
fixed seed, so every run produces the same data.

    python scripts/generate_data.py

The data is synthetic but follows realistic SaaS behaviour:
  * accounts sign up every month (growing ~2% a month) on Basic, Pro or Enterprise
  * each account has a hidden "health" score that drifts over time;
    low health -> fewer active users, more support tickets, higher churn risk
  * a Basic price increase in Jul 2025 causes a churn spike ("Price too high")
  * a support backlog in Jan-Mar 2026 slows ticket resolution and raises churn

Deliberate data-quality issues are injected into the raw files so they can be
cleaned in Power Query (see docs/data-dictionary.md).
"""

import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

SEED = 42
FIRST_MONTH = date(2023, 1, 1)
LAST_MONTH = date(2026, 9, 1)
OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "raw"

PLANS = {
    # plan_id: (name, price per seat, seat range, base monthly churn probability)
    1: ("Basic", 15, (3, 15), 0.030),
    2: ("Pro", 35, (10, 60), 0.017),
    3: ("Enterprise", 60, (50, 300), 0.006),
}
BASIC_PRICE_INCREASE = (date(2025, 7, 1), 19)  # Basic goes from 15 to 19 per seat
SUPPORT_BACKLOG = (date(2026, 1, 1), date(2026, 3, 1))

REGIONS = [("North America", 0.42, 1.0), ("EMEA", 0.30, 0.9), ("APAC", 0.18, 1.25), ("LATAM", 0.10, 1.15)]
INDUSTRIES = ["Retail", "Healthcare", "Finance", "Manufacturing", "Education", "Technology", "Logistics", "Media"]
SIZES = ["1-50", "51-200", "201-1000", "1000+"]
CHANNELS = [("Organic Search", 0.35, 0.95), ("Paid Ads", 0.25, 1.35), ("Partner", 0.20, 0.75), ("Outbound Sales", 0.20, 0.9)]

REASONS = [
    ("PRC", "Price too high", "Price"),
    ("BUD", "Budget cuts", "Price"),
    ("FEA", "Missing features", "Product"),
    ("BUG", "Product bugs / reliability", "Product"),
    ("SUP", "Poor support experience", "Service"),
    ("ONB", "Difficult onboarding", "Service"),
    ("CMP", "Moved to a competitor", "Competitor"),
    ("CLS", "Business closed", "Other"),
]

NAME_A = ["Blue", "North", "Silver", "Bright", "Clear", "Iron", "Green", "Swift", "Summit", "Harbor", "Pine", "Atlas",
          "Coral", "Echo", "Granite", "Maple", "Nova", "Orbit", "Prime", "Quartz", "River", "Sage", "Terra", "Vertex"]
NAME_B = ["field", "stone", "wave", "path", "point", "line", "bridge", "gate", "works", "craft", "peak", "forge"]
NAME_C = ["Labs", "Group", "Partners", "Systems", "Co", "Logistics", "Health", "Retail", "Studios", "Analytics", "Foods", "Energy"]


def month_range(start, end):
    months, current = [], start
    while current <= end:
        months.append(current)
        current = date(current.year + current.month // 12, current.month % 12 + 1, 1)
    return months


def days_in_month(month_start):
    following = date(month_start.year + month_start.month // 12, month_start.month % 12 + 1, 1)
    return (following - month_start).days


def random_day(rng, month_start):
    return month_start + timedelta(days=rng.randrange(days_in_month(month_start)))


def weighted(rng, items):
    """Pick from [(value, weight, ...)] by weight."""
    return rng.choices(items, weights=[item[1] for item in items])[0]


def poisson(rng, lam):
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def price_per_seat(plan_id, month):
    name, price, _, _ = PLANS[plan_id]
    if name == "Basic" and month >= BASIC_PRICE_INCREASE[0]:
        return BASIC_PRICE_INCREASE[1]
    return price


def pick_reason(rng, account, month, recent_tickets):
    if account["plan_id"] == 1 and BASIC_PRICE_INCREASE[0] <= month <= date(2025, 10, 1) and rng.random() < 0.6:
        return "PRC"
    if SUPPORT_BACKLOG[0] <= month <= date(2026, 4, 1) and recent_tickets >= 2 and rng.random() < 0.55:
        return "SUP"
    if account["health"] < 0.35 and rng.random() < 0.5:
        return rng.choice(["BUG", "FEA", "SUP"])
    weights = {"PRC": 18, "BUD": 14, "FEA": 16, "BUG": 10, "SUP": 10, "ONB": 8, "CMP": 18, "CLS": 6}
    if account["tenure"] <= 3:
        weights["ONB"] += 25
    return rng.choices(list(weights), weights=list(weights.values()))[0]


def simulate(rng):
    months = month_range(FIRST_MONTH, LAST_MONTH)
    accounts, subscriptions, churns, tickets, usage = [], [], [], [], []
    active = []
    next_account_id, next_ticket_id = 1001, 500001
    used_names = set()

    for index, month in enumerate(months):
        # 1. New sign-ups this month
        for _ in range(round(40 * 1.02 ** index * rng.uniform(0.85, 1.15))):
            plan_id = rng.choices([1, 2, 3], weights=[55, 35, 10])[0]
            seat_low, seat_high = PLANS[plan_id][2]
            region = weighted(rng, REGIONS)
            channel = weighted(rng, CHANNELS)
            while True:
                name = f"{rng.choice(NAME_A)}{rng.choice(NAME_B)} {rng.choice(NAME_C)}"
                if name not in used_names:
                    used_names.add(name)
                    break
            account = {
                "account_id": next_account_id,
                "account_name": name,
                "industry": rng.choice(INDUSTRIES),
                "region": region[0],
                "region_risk": region[2],
                "company_size": rng.choices(SIZES, weights=[40, 30, 20, 10] if plan_id < 3 else [5, 20, 40, 35])[0],
                "channel": channel[0],
                "channel_risk": channel[2],
                "signup_date": random_day(rng, month),
                "plan_id": plan_id,
                "seats": rng.randint(seat_low, seat_high),
                "health": rng.uniform(0.45, 0.95),
                "tenure": 0,
                "mrr": 0,
                "new": True,
                "recent_tickets": [],
            }
            next_account_id += 1
            accounts.append(account)
            active.append(account)

        still_active = []
        for account in active:
            account["tenure"] += 1
            # Health drifts, pulled gently back toward 0.7
            account["health"] += rng.gauss(0, 0.07) + (0.7 - account["health"]) * 0.05
            if rng.random() < 0.01:
                account["health"] -= 0.3  # occasional shock (reorg, champion leaves)
            account["health"] = min(1.0, max(0.05, account["health"]))

            # Support tickets this month (generated first so they can drive churn)
            backlog = SUPPORT_BACKLOG[0] <= month <= SUPPORT_BACKLOG[1]
            lam = 0.15 + 1.6 * (1 - account["health"]) + (0.6 if account["plan_id"] == 3 else 0)
            month_tickets = poisson(rng, lam)
            for _ in range(month_tickets):
                created = random_day(rng, month)
                priority = rng.choices(["Low", "Medium", "High", "Urgent"], weights=[35, 40, 20, 5])[0]
                hours = rng.lognormvariate(math.log(14 if backlog else 6), 0.8)
                is_open = month == LAST_MONTH and rng.random() < 0.35 or rng.random() < 0.02
                csat = None
                if not is_open:
                    csat = max(1, min(5, round(5 - hours / 12 + rng.gauss(0, 0.8))))
                tickets.append({
                    "ticket_id": next_ticket_id,
                    "account_id": account["account_id"],
                    "created_date": created,
                    "priority": priority,
                    "category": rng.choices(["How-to", "Bug", "Billing", "Feature request", "Outage"],
                                            weights=[35, 25, 15, 18, 7])[0],
                    "resolution_hours": None if is_open else round(hours, 1),
                    "csat": csat,
                })
                next_ticket_id += 1
            account["recent_tickets"] = (account["recent_tickets"] + [month_tickets])[-3:]
            recent = sum(account["recent_tickets"])

            prev_mrr = account["mrr"]
            movement = "Flat"

            if account["new"]:
                account["new"] = False
                movement = "New"
            else:
                # Churn decision
                p = PLANS[account["plan_id"]][3]
                p *= 1.7 if account["tenure"] <= 4 else 1.0
                p *= 2.8 if account["health"] < 0.35 else 1.4 if account["health"] < 0.55 else 0.6
                p *= account["region_risk"] * account["channel_risk"]
                if account["plan_id"] == 1 and BASIC_PRICE_INCREASE[0] <= month <= date(2025, 9, 1):
                    p *= 2.2
                if SUPPORT_BACKLOG[0] <= month <= date(2026, 4, 1) and recent >= 2:
                    p *= 1.8
                if rng.random() < p:
                    reason = pick_reason(rng, account, month, recent)
                    churns.append({
                        "account_id": account["account_id"],
                        "plan_id": account["plan_id"],
                        "churn_date": random_day(rng, month),
                        "reason_code": reason,
                        "mrr_lost": prev_mrr,
                    })
                    subscriptions.append({
                        "account_id": account["account_id"], "month_start": month,
                        "plan_id": account["plan_id"], "seats": 0, "mrr": 0,
                        "mrr_change": -prev_mrr, "movement_type": "Churn",
                    })
                    continue

                # Seat or plan changes
                roll = rng.random()
                if roll < 0.03 + 0.03 * (account["health"] > 0.75):
                    account["seats"] = math.ceil(account["seats"] * rng.uniform(1.1, 1.4))
                elif roll < 0.07 and account["plan_id"] < 3 and account["health"] > 0.7:
                    account["plan_id"] += 1
                    account["seats"] = max(account["seats"], PLANS[account["plan_id"]][2][0])
                elif roll < 0.10 + 0.04 * (account["health"] < 0.5):
                    account["seats"] = max(1, math.floor(account["seats"] * rng.uniform(0.7, 0.9)))

            account["mrr"] = account["seats"] * price_per_seat(account["plan_id"], month)
            change = account["mrr"] - prev_mrr
            if movement != "New":
                movement = "Expansion" if change > 0 else "Contraction" if change < 0 else "Flat"
            subscriptions.append({
                "account_id": account["account_id"], "month_start": month,
                "plan_id": account["plan_id"], "seats": account["seats"], "mrr": account["mrr"],
                "mrr_change": change, "movement_type": movement,
            })

            active_users = max(0, round(account["seats"] * account["health"] * rng.uniform(0.85, 1.1)))
            active_users = min(active_users, account["seats"])
            usage.append({
                "account_id": account["account_id"], "month_start": month,
                "active_users": active_users, "logins": active_users * rng.randint(8, 25),
            })
            still_active.append(account)
        active = still_active

    return accounts, subscriptions, churns, tickets, usage


def messy_accounts(rng, accounts):
    """Return account rows with deliberate data-quality problems."""
    region_variants = {
        "North America": ["North America", "North America", "N. America", "NA", "north america "],
        "EMEA": ["EMEA", "EMEA", "Europe", "emea"],
        "APAC": ["APAC", "APAC", "Asia Pacific", "apac "],
        "LATAM": ["LATAM", "LATAM", "Latin America"],
    }
    rows = []
    for account in accounts:
        signup = account["signup_date"]
        rows.append({
            "account_id": account["account_id"],
            "account_name": account["account_name"] + ("  " if rng.random() < 0.05 else ""),
            "industry": account["industry"].lower() if rng.random() < 0.06 else account["industry"],
            "region": rng.choice(region_variants[account["region"]]),
            "company_size": "" if rng.random() < 0.04 else account["company_size"],
            "acquisition_channel": account["channel"],
            "signup_date": signup.strftime("%d/%m/%Y") if rng.random() < 0.05 else signup.isoformat(),
        })
    duplicates = [dict(row) for row in rng.sample(rows, k=len(rows) // 60)]
    rows.extend(duplicates)
    rng.shuffle(rows)
    return rows


def write_csv(name, fieldnames, rows):
    with open(OUT_DIR / name, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({key: "" if row.get(key) is None else row[key] for key in fieldnames})


def main():
    rng = random.Random(SEED)
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    accounts, subscriptions, churns, tickets, usage = simulate(rng)

    write_csv("plans.csv", ["plan_id", "plan_name", "price_per_seat"],
              [{"plan_id": pid, "plan_name": p[0], "price_per_seat": price_per_seat(pid, LAST_MONTH)}
               for pid, p in PLANS.items()])
    write_csv("churn_reasons.csv", ["reason_code", "reason", "reason_group"],
              [{"reason_code": c, "reason": r, "reason_group": g} for c, r, g in REASONS])
    write_csv("accounts.csv",
              ["account_id", "account_name", "industry", "region", "company_size", "acquisition_channel", "signup_date"],
              messy_accounts(rng, accounts))
    write_csv("subscriptions_monthly.csv",
              ["account_id", "month_start", "plan_id", "seats", "mrr", "mrr_change", "movement_type"], subscriptions)
    for churn in churns:
        if rng.random() < 0.08:
            churn["reason_code"] = ""  # reason not captured
    write_csv("churn_events.csv", ["account_id", "plan_id", "churn_date", "reason_code", "mrr_lost"], churns)
    for ticket in tickets:
        if rng.random() < 0.07:
            ticket["priority"] = rng.choice([ticket["priority"].upper(), ticket["priority"].lower(), f" {ticket['priority']}"])
    write_csv("support_tickets.csv",
              ["ticket_id", "account_id", "created_date", "priority", "category", "resolution_hours", "csat"], tickets)
    write_csv("usage_monthly.csv", ["account_id", "month_start", "active_users", "logins"], usage)

    print(f"accounts: {len(accounts):,} | subscription rows: {len(subscriptions):,} | churn events: {len(churns):,} "
          f"| tickets: {len(tickets):,} | usage rows: {len(usage):,}")
    print(f"Written to {OUT_DIR}")


if __name__ == "__main__":
    main()
