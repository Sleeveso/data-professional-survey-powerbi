// Query name : dim_job
let
    Source   = Table.SelectColumns(fact_survey, {"Job Title"}),
    Distinct = Table.Distinct(Source),
    Sorted   = Table.Sort(Distinct, {{"Job Title", Order.Ascending}})
in
    Sorted
