// Query name : dim_date   (continuous calendar covering the survey window)
let
    StartDate = List.Min(fact_survey[Survey Date]),
    EndDate   = List.Max(fact_survey[Survey Date]),
    NumDays   = Duration.Days(EndDate - StartDate) + 1,
    Dates     = List.Dates(StartDate, NumDays, #duration(1, 0, 0, 0)),
    AsTable   = Table.FromList(Dates, Splitter.SplitByNothing(), {"Date"}, null, ExtraValues.Error),
    TypedDate = Table.TransformColumnTypes(AsTable, {{"Date", type date}}),
    Year      = Table.AddColumn(TypedDate, "Year", each Date.Year([Date]), Int64.Type),
    MonthNum  = Table.AddColumn(Year, "Month Number", each Date.Month([Date]), Int64.Type),
    MonthName = Table.AddColumn(MonthNum, "Month Name", each Date.MonthName([Date], "en-US"), type text),
    DayOfMon  = Table.AddColumn(MonthName, "Day of Month", each Date.Day([Date]), Int64.Type),
    DowNum    = Table.AddColumn(DayOfMon, "Day of Week Number", each Date.DayOfWeek([Date], Day.Monday) + 1, Int64.Type),
    DowName   = Table.AddColumn(DowNum, "Day of Week", each Date.DayOfWeekName([Date], "en-US"), type text),
    Weekend   = Table.AddColumn(DowName, "Is Weekend", each [Day of Week Number] >= 6, type logical),
    SurveyDay = Table.AddIndexColumn(Weekend, "Survey Day Number", 1, 1, Int64.Type)
in
    SurveyDay
