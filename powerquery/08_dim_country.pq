// Query name : dim_country   (World Bank region via data/reference/country_region.csv)
let
    Source   = Table.SelectColumns(fact_survey, {"Country"}),
    Distinct = Table.Distinct(Source),
    Region   = fn_LoadRef("country_region.csv"),
    Joined   = Table.NestedJoin(Distinct, {"Country"}, Region, {"Country"}, "r", JoinKind.LeftOuter),
    Expanded = Table.ExpandTableColumn(Joined, "r", {"Region"}),
    Sorted   = Table.Sort(Expanded, {{"Country", Order.Ascending}})
in
    Sorted
