// Query name : fn_CleanCountry   (function) - mirrors clean_country() in scripts/clean_data.py
(value as nullable text) as text =>
let
    v      = Text.Trim(value ?? ""),
    listed = {"United States", "India", "United Kingdom", "Canada"},
    d      = fn_OtherDetail(v),
    key    = Text.Lower(d),
    fixes  = {
        {"uae", "United Arab Emirates"}, {"perú", "Peru"},
        {"republic democratic of congo", "Democratic Republic of the Congo"},
        {"africa (nigeria)", "Nigeria"}, {"aisa", "Unknown"}, {"argentine", "Argentina"},
        {"austr", "Australia"}, {"brazik", "Brazil"}, {"fin", "Finland"}, {"ire", "Ireland"},
        {"irel", "Ireland"}, {"kenua", "Kenya"}, {"leba", "Lebanon"}, {"portugsl", "Portugal"},
        {"sg", "Singapore"}, {"uzb", "Uzbekistan"}, {"antigua", "Antigua and Barbuda"},
        {"macedonia", "North Macedonia"}
    },
    match  = List.Select(fixes, each _{0} = key),
    result =
        if List.Contains(listed, v) then v
        else if d = "" then "Unknown"
        else if List.Count(match) > 0 then match{0}{1}
        else Text.Proper(d)
in
    result
