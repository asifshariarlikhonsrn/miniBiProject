// FactSubscriptionMonthly: one row per account per month (MRR snapshot + the movement that produced it)
// Adds MonthsSinceSignup for the cohort-retention matrix
let
    Source = Csv.Document(File.Contents(DataFolder & "subscriptions_monthly.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"account_id", Int64.Type}, {"month_start", type date}, {"plan_id", Int64.Type}, {"seats", Int64.Type},
        {"mrr", Currency.Type}, {"mrr_change", Currency.Type}, {"movement_type", type text}
    }, "en-US"),

    // Look up each account's cohort month from DimAccount
    Merged = Table.NestedJoin(Typed, {"account_id"}, DimAccount, {"AccountID"}, "Account", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Merged, "Account", {"CohortMonth"}),
    AddMonthsSince = Table.AddColumn(Expanded, "MonthsSinceSignup", each
        (Date.Year([month_start]) - Date.Year([CohortMonth])) * 12 + Date.Month([month_start]) - Date.Month([CohortMonth]),
        Int64.Type),
    Removed = Table.RemoveColumns(AddMonthsSince, {"CohortMonth"}),

    Renamed = Table.RenameColumns(Removed, {
        {"account_id", "AccountID"}, {"month_start", "MonthStart"}, {"plan_id", "PlanID"}, {"seats", "Seats"},
        {"mrr", "MRR"}, {"mrr_change", "MRRChange"}, {"movement_type", "MovementType"}
    })
in
    Renamed
