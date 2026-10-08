// FactSupportTicket: one row per ticket
// Fixes: inconsistent priority casing/spaces. Open tickets have no resolution time or CSAT (kept as null)
let
    Source = Csv.Document(File.Contents(DataFolder & "support_tickets.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),
    FixPriority = Table.TransformColumns(Promoted, {{"priority", each Text.Proper(Text.Trim(_)), type text}}),
    Typed = Table.TransformColumnTypes(FixPriority, {
        {"ticket_id", Int64.Type}, {"account_id", Int64.Type}, {"created_date", type date}, {"category", type text},
        {"resolution_hours", type number}, {"csat", Int64.Type}
    }, "en-US"),
    AddIsOpen = Table.AddColumn(Typed, "IsOpen", each [resolution_hours] = null, type logical),
    Renamed = Table.RenameColumns(AddIsOpen, {
        {"ticket_id", "TicketID"}, {"account_id", "AccountID"}, {"created_date", "CreatedDate"}, {"priority", "Priority"},
        {"category", "Category"}, {"resolution_hours", "ResolutionHours"}, {"csat", "CSAT"}
    })
in
    Renamed
