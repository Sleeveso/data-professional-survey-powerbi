// Query name : fn_LoadRef   (function) - loads a CSV from /data/reference
(fileName as text) as table =>
let
    Path     = Text.TrimEnd(pDataFolder, "\") & "\data\reference\" & fileName,
    Source   = Csv.Document(File.Contents(Path), [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]),
    Promoted = Table.PromoteHeaders(Source, [PromoteAllScalars = true])
in
    Promoted
