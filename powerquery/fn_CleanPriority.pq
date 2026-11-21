// Query name : fn_CleanPriority   (function) - mirrors clean_priority() in scripts/clean_data.py
(value as nullable text) as text =>
let
    v      = Text.Trim(value ?? ""),
    listed = {"Better Salary", "Remote Work", "Good Work/Life Balance", "Good Culture"},
    d      = Text.Lower(fn_OtherDetail(v)),
    result =
        if List.Contains(listed, v) then v
        else if d = "" then "Other"
        else if fn_HasAny(d, {"all of", "combination", "mix", "both"}) then "Multiple / All of the Above"
        else if fn_HasAny(d, {"learn", "growth", "advanc", "develop", "opportunit", "mentor", "skills", "challeng", "exposure"}) then "Growth & Learning"
        else "Other"
in
    result
