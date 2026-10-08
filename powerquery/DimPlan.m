// DimPlan: one row per plan (current list price per seat)
let
    Source = Csv.Document(File.Contents(DataFolder & "plans.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    Typed = Table.TransformColumnTypes(Promoted, {{"plan_id", Int64.Type}, {"plan_name", type text}, {"price_per_seat", Currency.Type}}),
    Renamed = Table.RenameColumns(Typed, {{"plan_id", "PlanID"}, {"plan_name", "PlanName"}, {"price_per_seat", "PricePerSeat"}})
in
    Renamed
