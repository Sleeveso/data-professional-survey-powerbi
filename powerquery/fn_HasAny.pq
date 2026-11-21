// Query name : fn_HasAny   (function) - TRUE if text contains any keyword in the list
(text as text, keywords as list) as logical =>
    List.AnyTrue(List.Transform(keywords, each Text.Contains(text, _)))
