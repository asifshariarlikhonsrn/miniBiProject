// DimDate: one continuous row per day, covering whole years from the first to the last month in the data
// After loading: Table tools > Mark as date table (Date column); sort MonthName by MonthSort, YearMonth by YearMonthSort
let
    FirstMonth = List.Min(FactSubscriptionMonthly[MonthStart]),
    LastMonth = List.Max(FactSubscriptionMonthly[MonthStart]),
    StartDate = Date.StartOfYear(FirstMonth),
    EndDate = Date.EndOfYear(LastMonth),
    Dates = List.Dates(StartDate, Duration.Days(EndDate - StartDate) + 1, #duration(1, 0, 0, 0)),
    ToTable = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}),
    Typed = Table.TransformColumnTypes(ToTable, {{"Date", type date}}),
    AddYear = Table.AddColumn(Typed, "Year", each Date.Year([Date]), Int64.Type),
    AddQuarter = Table.AddColumn(AddYear, "Quarter", each "Q" & Text.From(Date.QuarterOfYear([Date])), type text),
    AddMonthStart = Table.AddColumn(AddQuarter, "MonthStart", each Date.StartOfMonth([Date]), type date),
    AddMonthName = Table.AddColumn(AddMonthStart, "MonthName", each Date.ToText([Date], [Format = "MMM", Culture = "en-US"]), type text),
    AddMonthSort = Table.AddColumn(AddMonthName, "MonthSort", each Date.Month([Date]), Int64.Type),
    AddYearMonth = Table.AddColumn(AddMonthSort, "YearMonth", each Date.ToText([Date], [Format = "MMM yyyy", Culture = "en-US"]), type text),
    AddYearMonthSort = Table.AddColumn(AddYearMonth, "YearMonthSort", each Date.Year([Date]) * 100 + Date.Month([Date]), Int64.Type),
    // Flag months that are in the data, so visuals can hide the empty months after the last one
    AddInData = Table.AddColumn(AddYearMonthSort, "IsInData", each [MonthStart] <= LastMonth, type logical)
in
    AddInData
