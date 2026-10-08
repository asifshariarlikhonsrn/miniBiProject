// DimChurnReason: one row per reason, plus a "Not stated" row for churn events with no reason captured
let
    Source = Csv.Document(File.Contents(DataFolder & "churn_reasons.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    AddNotStated = Table.InsertRows(Promoted, Table.RowCount(Promoted), {
        [reason_code = "NS", reason = "Not stated", reason_group = "Unknown"]
    }),
    Typed = Table.TransformColumnTypes(AddNotStated, {{"reason_code", type text}, {"reason", type text}, {"reason_group", type text}}),
    Renamed = Table.RenameColumns(Typed, {{"reason_code", "ReasonID"}, {"reason", "Reason"}, {"reason_group", "ReasonGroup"}})
in
    Renamed
