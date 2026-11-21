// Query name : dim_education
let
    Source = fn_LoadRef("education_levels.csv"),
    Typed  = Table.TransformColumnTypes(Source, {{"Education Level", type text}, {"Education Sort", Int64.Type}}, "en-US")
in
    Typed
