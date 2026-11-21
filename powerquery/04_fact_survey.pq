// Query name : fact_survey   (grain: one row per survey respondent)
// Mirrors build() in scripts/clean_data.py - keep both in sync.
let
    Source = Raw_Survey,

    // ---- 1. Keep only useful columns (drops Email, Browser, OS, City, Country, Referrer) ----
    q6Prefix = "Q6 - How Happy are you in your Current Position with the following? (",
    factors  = {"Salary", "Work/Life Balance", "Coworkers", "Management", "Upward Mobility", "Learning New Things"},
    q6Cols   = List.Transform(factors, each q6Prefix & _ & ")"),
    Keep = Table.SelectColumns(Source, List.Combine({
        {"Unique ID", "Date Taken (America/New_York)", "Time Taken (America/New_York)", "Time Spent",
         "Q1 - Which Title Best Fits your Current Role?", "Q2 - Did you switch careers into Data?",
         "Q3 - Current Yearly Salary (in USD)", "Q4 - What Industry do you work in?",
         "Q5 - Favorite Programming Language",
         "Q7 - How difficult was it for you to break into Data?",
         "Q8 - If you were to look for a new job today, what would be the most important thing to you?",
         "Q9 - Male/Female?", "Q10 - Current Age", "Q11 - Which Country do you live in?",
         "Q12 - Highest Level of Education", "Q13 - Ethnicity"},
        q6Cols})),

    // ---- 2. Rename to short, stable names ----
    Renamed = Table.RenameColumns(Keep, List.Combine({
        {{"Unique ID", "Respondent ID"}, {"Date Taken (America/New_York)", "Date Taken"},
         {"Time Taken (America/New_York)", "Time Taken"},
         {"Q1 - Which Title Best Fits your Current Role?", "Job Title Raw"},
         {"Q2 - Did you switch careers into Data?", "Switched Careers"},
         {"Q3 - Current Yearly Salary (in USD)", "Salary Band"},
         {"Q4 - What Industry do you work in?", "Industry Raw"},
         {"Q5 - Favorite Programming Language", "Language Raw"},
         {"Q7 - How difficult was it for you to break into Data?", "Break-in Difficulty"},
         {"Q8 - If you were to look for a new job today, what would be the most important thing to you?", "Priority Raw"},
         {"Q9 - Male/Female?", "Gender"}, {"Q10 - Current Age", "Age Raw"},
         {"Q11 - Which Country do you live in?", "Country Raw"},
         {"Q12 - Highest Level of Education", "Education Level"}, {"Q13 - Ethnicity", "Ethnicity Raw"}},
        List.Transform(factors, each {q6Prefix & _ & ")", "Happiness - " & _})
    })),

    // ---- 3. Keys, dates, time ----
    AddKey   = Table.AddIndexColumn(Renamed, "Respondent Key", 1, 1, Int64.Type),
    AddDate  = Table.AddColumn(AddKey, "Survey Date",
                   each Date.FromText(Text.Trim([Date Taken]), [Format = "M/d/yyyy", Culture = "en-US"]), type date),
    AddHour  = Table.AddColumn(AddDate, "Survey Hour",
                   each Number.FromText(Text.BeforeDelimiter(Text.Trim([Time Taken]), ":")), Int64.Type),
    AddSecs  = Table.AddColumn(AddHour, "Time Spent (Sec)", each fn_DurationToSeconds([Time Spent]), Int64.Type),
    AddQual  = Table.AddColumn(AddSecs, "Response Quality",
                   each if [#"Time Spent (Sec)"] < 30 then "Speeder (<30s)"
                        else if [#"Time Spent (Sec)"] > 1800 then "Idle Session (>30 min)"
                        else "Normal", type text),

    // ---- 4. Standardise free-text categories ----
    AddJob   = Table.AddColumn(AddQual, "Job Title",         each fn_CleanJob([Job Title Raw]), type text),
    AddInd   = Table.AddColumn(AddJob,  "Industry",          each fn_CleanIndustry([Industry Raw]), type text),
    AddCty   = Table.AddColumn(AddInd,  "Country",           each fn_CleanCountry([Country Raw]), type text),
    AddLang  = Table.AddColumn(AddCty,  "Favorite Language", each fn_CleanLanguage([Language Raw]), type text),
    AddPrio  = Table.AddColumn(AddLang, "Top Job Priority",  each fn_CleanPriority([Priority Raw]), type text),
    AddEth   = Table.AddColumn(AddPrio, "Ethnicity",         each fn_CleanEthnicity([Ethnicity Raw]), type text),
    FixEdu   = Table.TransformColumns(AddEth, {{"Education Level", each if _ = null then "Not Provided" else Text.Trim(_), type text}}),

    // ---- 5. Enrich from reference dimensions (salary midpoint, difficulty score) ----
    JoinSal  = Table.NestedJoin(FixEdu, {"Salary Band"}, dim_salary, {"Salary Band"}, "sal", JoinKind.LeftOuter),
    ExpSal   = Table.ExpandTableColumn(JoinSal, "sal", {"Salary Midpoint"}),
    JoinDif  = Table.NestedJoin(ExpSal, {"Break-in Difficulty"}, dim_difficulty, {"Break-in Difficulty"}, "dif", JoinKind.LeftOuter),
    ExpDif   = Table.ExpandTableColumn(JoinDif, "dif", {"Difficulty Score"}),

    // ---- 6. Age: keep plausible values only (18-80); 92 is a data-entry error ----
    AddAge   = Table.AddColumn(ExpDif, "Age",
                   each let a = try Number.From([Age Raw]) otherwise null
                        in if a <> null and a >= 18 and a <= 80 then a else null, Int64.Type),
    AddAgeG  = Table.AddColumn(AddAge, "Age Group", each fn_AgeGroup([Age]), type text),

    // ---- 7. Happiness: blanks stay null; respondent-level average + straight-line flag ----
    TypeHap  = Table.TransformColumnTypes(AddAgeG, List.Transform(factors, each {"Happiness - " & _, Int64.Type}), "en-US"),
    hapNames = List.Transform(factors, each "Happiness - " & _),
    AddOverall = Table.AddColumn(TypeHap, "Overall Happiness",
                   each let vals = List.RemoveNulls(Record.FieldValues(Record.SelectFields(_, hapNames)))
                        in if List.Count(vals) = 0 then null else Number.Round(List.Average(vals), 3), type number),
    AddStraight = Table.AddColumn(AddOverall, "Straight-lined Happiness",
                   each let vals = List.RemoveNulls(Record.FieldValues(Record.SelectFields(_, hapNames)))
                        in List.Count(List.Distinct(vals)) = 1, type logical),

    // ---- 8. Final column order & types ----
    Final = Table.SelectColumns(AddStraight, List.Combine({
        {"Respondent Key", "Respondent ID", "Survey Date", "Survey Hour", "Time Spent (Sec)", "Response Quality",
         "Job Title", "Industry", "Country", "Education Level", "Salary Band", "Salary Midpoint", "Age", "Age Group",
         "Gender", "Ethnicity", "Favorite Language", "Switched Careers", "Break-in Difficulty", "Difficulty Score",
         "Top Job Priority"},
        hapNames, {"Overall Happiness", "Straight-lined Happiness"}}))
in
    Final
