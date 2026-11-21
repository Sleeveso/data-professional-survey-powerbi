// Query name : dim_salary
let
    Source = fn_LoadRef("salary_bands.csv"),
    Typed  = Table.TransformColumnTypes(Source, {
        {"Salary Band", type text}, {"Salary Sort", Int64.Type}, {"Salary Min", Int64.Type},
        {"Salary Max", Int64.Type}, {"Salary Midpoint", Int64.Type}, {"Salary Tier", type text}
    }, "en-US")
in
    Typed
