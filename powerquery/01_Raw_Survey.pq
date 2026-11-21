// Query name : Raw_Survey   (Disable load - staging only)
// Reads the untouched workbook. Date / time columns are TEXT in the source file.
let
    Path     = Text.TrimEnd(pDataFolder, "\") & "\data\raw\Data_Professional_Survey.xlsx",
    Source   = Excel.Workbook(File.Contents(Path), null, true),
    Sheet    = Source{[Item = "Data Professional Survey", Kind = "Sheet"]}[Data],
    Promoted = Table.PromoteHeaders(Sheet, [PromoteAllScalars = true])
in
    Promoted
