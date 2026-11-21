// Query name : fn_CleanIndustry   (function) - mirrors clean_industry() in scripts/clean_data.py
(value as nullable text) as text =>
let
    v      = Text.Trim(value ?? ""),
    listed = {"Tech", "Finance", "Healthcare", "Education", "Telecommunication", "Construction", "Real Estate", "Agriculture"},
    d      = Text.Lower(fn_OtherDetail(v)),
    result =
        if List.Contains(listed, v) then v
        else if d = "" then "Other"
        else if fn_HasAny(d, {"not working", "studying", "none"}) then "Not Working / Student"
        else if Text.StartsWith(d, "cons") then "Consulting"
        else if Text.Contains(d, "insurance") then "Finance"
        else if Text.Contains(d, "biotech") then "Healthcare"
        else if fn_HasAny(d, {"retail", "wholesale", "consumer", "ecom", "e-com"}) then "Retail & E-commerce"
        else if fn_HasAny(d, {"manuf", "automotive", "aerospace", "semiconductor", "food"}) then "Manufacturing"
        else if fn_HasAny(d, {"logistic", "supply chain", "distribution", "aviation"}) then "Logistics & Supply Chain"
        else if fn_HasAny(d, {"energy", "oil and gas", "utili"}) then "Energy & Utilities"
        else if fn_HasAny(d, {"market", "advertis"}) then "Marketing & Advertising"
        else if fn_HasAny(d, {"government", "nonprofit"}) then "Government & Nonprofit"
        else "Other"
in
    result
