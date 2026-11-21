// Query name : fn_DurationToSeconds   (function) - 'h:mm:ss' text -> seconds
(value as nullable text) as nullable number =>
let
    parts = Text.Split(Text.Trim(value ?? ""), ":")
in
    if List.Count(parts) <> 3 then null
    else Number.FromText(parts{0}) * 3600 + Number.FromText(parts{1}) * 60 + Number.FromText(parts{2})
