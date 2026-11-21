// Query name : fn_OtherDetail   (function)
// 'Other (Please Specify):Retail' -> 'Retail'   |   'Tech' -> ''   |   'Other' -> ''
(value as nullable text) as text =>
let
    v       = Text.Trim(value ?? ""),
    isOther = Text.StartsWith(v, "Other"),
    detail  = if not isOther then ""
              else if Text.Contains(v, ":") then Text.Trim(Text.AfterDelimiter(v, ":"))
              else ""
in
    detail
