// Query name : fn_CleanEthnicity   (function) - mirrors clean_ethnicity() in scripts/clean_data.py
(value as nullable text) as text =>
let
    v      = Text.Trim(value ?? ""),
    listed = {"White or Caucasian", "Asian or Asian American", "Black or African American", "Hispanic or Latino",
              "American Indian or Alaska Native", "Native Hawaiian or other Pacific Islander"},
    d      = Text.Lower(fn_OtherDetail(v)),
    result =
        if List.Contains(listed, v) then v
        else if d = "" then "Other / Not Specified"
        else if fn_HasAny(d, {"half", "mixed", "bi-racial"}) then "Mixed / Multiracial"
        else if fn_HasAny(d, {"indian", "asian", "pakistani", "bangladeshi", "dravidian", "malay", "melayu"}) then "Asian or Asian American"
        else if fn_HasAny(d, {"african", "black"}) or d = "bla" or d = "nigeria" then "Black or African American"
        else "Other / Not Specified"
in
    result
