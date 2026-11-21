// Query name : dim_industry
let
    Source   = Table.SelectColumns(fact_survey, {"Industry"}),
    Distinct = Table.Distinct(Source),
    Sorted   = Table.Sort(Distinct, {{"Industry", Order.Ascending}})
in
    Sorted
