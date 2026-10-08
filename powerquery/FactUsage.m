// FactUsage: one row per account per month
let
    Source = Csv.Document(File.Contents(DataFolder & "usage_monthly.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {
        {"account_id", Int64.Type}, {"month_start", type date}, {"active_users", Int64.Type}, {"logins", Int64.Type}
    }, "en-US"),
    Renamed = Table.RenameColumns(Typed, {
        {"account_id", "AccountID"}, {"month_start", "MonthStart"}, {"active_users", "ActiveUsers"}, {"logins", "Logins"}
    })
in
    Renamed
