// Query name : fn_CleanLanguage   (function) - mirrors clean_language() in scripts/clean_data.py
(value as nullable text) as text =>
let
    v      = Text.Trim(value ?? ""),
    listed = {"Python", "R", "C/C++", "JavaScript", "Java"},
    d      = Text.Lower(fn_OtherDetail(v)),
    result =
        if List.Contains(listed, v) then v
        else if d = "" then "Other"
        else if Text.Contains(d, "sql") then "SQL"
        else if fn_HasAny(d, {"excel", "vba"}) then "Excel / VBA"
        else if fn_HasAny(d, {"dax", "power bi"}) then "DAX / Power BI"
        else if d = "na" or fn_HasAny(d, {"none", "dont", "don't", "don’t", "do not", "unknown", "not use", "started", "require", "presentations"}) then "None / Not Applicable"
        else "Other"
in
    result
