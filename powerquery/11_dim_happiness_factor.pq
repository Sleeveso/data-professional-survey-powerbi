// Query name : dim_happiness_factor
let
    Source = fn_LoadRef("happiness_factors.csv"),
    Typed  = Table.TransformColumnTypes(Source, {{"Happiness Factor", type text}, {"Factor Sort", Int64.Type}, {"Factor Group", type text}}, "en-US")
in
    Typed
