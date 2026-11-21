// Query name : fact_happiness   (grain: one row per respondent x happiness factor)
// UnpivotColumns drops null ratings automatically -> missing answers are never treated as 0.
let
    hapNames = {"Happiness - Salary", "Happiness - Work/Life Balance", "Happiness - Coworkers",
                "Happiness - Management", "Happiness - Upward Mobility", "Happiness - Learning New Things"},
    Source   = Table.SelectColumns(fact_survey, List.Combine({{"Respondent Key"}, hapNames})),
    Unpivot  = Table.UnpivotColumns(Source, {"Respondent Key"}, "Happiness Factor", "Happiness Score"),
    Clean    = Table.TransformColumns(Unpivot, {{"Happiness Factor", each Text.Replace(_, "Happiness - ", ""), type text}}),
    AddCat   = Table.AddColumn(Clean, "Happiness Category",
                   each if [Happiness Score] <= 3 then "Unhappy (0-3)"
                        else if [Happiness Score] <= 6 then "Neutral (4-6)"
                        else "Happy (7-10)", type text),
    Typed    = Table.TransformColumnTypes(AddCat, {{"Respondent Key", Int64.Type}, {"Happiness Score", Int64.Type}}),
    Sorted   = Table.Sort(Typed, {{"Respondent Key", Order.Ascending}, {"Happiness Factor", Order.Ascending}})
in
    Sorted
