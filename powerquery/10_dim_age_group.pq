// Query name : dim_age_group
let
    Source = fn_LoadRef("age_groups.csv"),
    Typed  = Table.TransformColumnTypes(Source, {{"Age Group", type text}, {"Age Group Sort", Int64.Type}}, "en-US")
in
    Typed
