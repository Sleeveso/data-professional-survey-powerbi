// Query name : dim_difficulty
let
    Source = fn_LoadRef("difficulty_levels.csv"),
    Typed  = Table.TransformColumnTypes(Source, {
        {"Break-in Difficulty", type text}, {"Difficulty Score", Int64.Type}, {"Difficulty Group", type text}
    }, "en-US")
in
    Typed
