// FactChurnEvent: one row per churned account. Blank reasons become "NS" (Not stated)
let
    Source = Csv.Document(File.Contents(DataFolder & "churn_events.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    FillReason = Table.ReplaceValue(Promoted, "", "NS", Replacer.ReplaceValue, {"reason_code"}),
    Typed = Table.TransformColumnTypes(FillReason, {
        {"account_id", Int64.Type}, {"plan_id", Int64.Type}, {"churn_date", type date}, {"reason_code", type text}, {"mrr_lost", Currency.Type}
    }, "en-US"),
    Renamed = Table.RenameColumns(Typed, {
        {"account_id", "AccountID"}, {"plan_id", "PlanID"}, {"churn_date", "ChurnDate"}, {"reason_code", "ReasonID"}, {"mrr_lost", "MRRLost"}
    })
in
    Renamed
