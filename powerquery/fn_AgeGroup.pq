// Query name : fn_AgeGroup   (function)
(age as nullable number) as text =>
    if age = null then "Unknown"
    else if age <= 24 then "18-24"
    else if age <= 29 then "25-29"
    else if age <= 34 then "30-34"
    else if age <= 39 then "35-39"
    else if age <= 44 then "40-44"
    else "45+"
