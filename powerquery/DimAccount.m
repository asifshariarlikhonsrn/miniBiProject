// DimAccount: one row per account, cleaned from accounts.csv
// Fixes: duplicate rows, region spelling variants, mixed date formats, stray spaces/casing, blank company size
let
    Source = Csv.Document(File.Contents(DataFolder & "accounts.csv"), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true]),

    // Standardise text: trim spaces, remove non-printing characters, fix casing
    CleanText = Table.TransformColumns(Promoted, {
        {"account_name", each Text.Trim(Text.Clean(_)), type text},
        {"industry", each Text.Proper(Text.Trim(_)), type text},
        {"region", each Text.Upper(Text.Trim(_)), type text},
        {"acquisition_channel", each Text.Trim(_), type text}
    }),

    // Map every region spelling to one value; anything unexpected becomes "Unknown" so it is easy to spot
    RegionMap = [
        #"NORTH AMERICA" = "North America", #"N. AMERICA" = "North America", NA = "North America",
        EMEA = "EMEA", EUROPE = "EMEA",
        APAC = "APAC", #"ASIA PACIFIC" = "APAC",
        LATAM = "LATAM", #"LATIN AMERICA" = "LATAM"
    ],
    FixRegion = Table.TransformColumns(CleanText, {{"region", each Record.FieldOrDefault(RegionMap, _, "Unknown"), type text}}),

    // Most dates are yyyy-MM-dd, some are dd/MM/yyyy
    ParseDate = (value as text) as date =>
        if Text.Contains(value, "/")
        then Date.FromText(value, [Format = "dd/MM/yyyy"])
        else Date.FromText(value, [Format = "yyyy-MM-dd"]),
    FixDates = Table.TransformColumns(FixRegion, {{"signup_date", ParseDate, type date}}),

    FixSize = Table.ReplaceValue(FixDates, "", "Unknown", Replacer.ReplaceValue, {"company_size"}),
    Typed = Table.TransformColumnTypes(FixSize, {{"account_id", Int64.Type}, {"company_size", type text}}),

    // Remove duplicate accounts (keeps the first row per account_id)
    Deduped = Table.Distinct(Typed, {"account_id"}),

    AddCohort = Table.AddColumn(Deduped, "CohortMonth", each Date.StartOfMonth([signup_date]), type date),
    Renamed = Table.RenameColumns(AddCohort, {
        {"account_id", "AccountID"}, {"account_name", "AccountName"}, {"industry", "Industry"},
        {"region", "Region"}, {"company_size", "CompanySize"}, {"acquisition_channel", "Channel"},
        {"signup_date", "SignupDate"}
    })
in
    Renamed
