local function has_class(element, name)
  for _, class_name in ipairs(element.classes) do
    if class_name == name then
      return true
    end
  end
  return false
end

function Span(element)
  if not FORMAT:match("latex") then
    return nil
  end

  local opening = nil
  if has_class(element, "book-question-label") then
    opening = "\\BookQuestionLabel{"
  elseif has_class(element, "book-question-prompt") then
    opening = "\\BookQuestionPrompt{"
  end

  if opening == nil then
    return nil
  end

  local content = pandoc.List({pandoc.RawInline("latex", opening)})
  content:extend(element.content)
  content:insert(pandoc.RawInline("latex", "}"))
  return content
end

function Image(element)
  if not FORMAT:match("latex") or not has_class(element, "book-question-image") then
    return nil
  end
  -- The former 30 mm size reduced the illustration to a decorative stamp.
  -- A 52 mm print width keeps the quiet hanji aesthetic while making the
  -- chapter symbol readable on an A5 page.
  element.attributes["width"] = "52mm"
  return pandoc.List({
    pandoc.RawInline("latex", "\\hfill{}"),
    element,
    pandoc.RawInline("latex", "\\hfill\\mbox{}"),
  })
end

function Div(element)
  if not FORMAT:match("latex") or not has_class(element, "book-question") then
    return nil
  end

  local blocks = pandoc.List({
    pandoc.RawBlock(
      "latex",
      "\\begin{tcolorbox}[enhanced,breakable,colback=questioncream,colframe=questionnavy,boxrule=0.7pt,leftrule=3.5pt,arc=2mm,left=4mm,right=4mm,top=3mm,bottom=3mm,before skip=10pt,after skip=12pt]"
    )
  })
  blocks:extend(element.content)
  blocks:insert(pandoc.RawBlock("latex", "\\end{tcolorbox}"))
  return blocks
end

function Table(element)
  local header_parts = {}
  for _, row in ipairs(element.head.rows) do
    for _, cell in ipairs(row.cells) do
      table.insert(header_parts, pandoc.utils.stringify(cell.contents))
    end
  end
  local header_text = table.concat(header_parts, " ")
  if not header_text:match("근거 번호") and not header_text:match("데이터 카드") then
    return nil
  end

  element.colspecs = {
    {pandoc.AlignCenter, 0.28},
    {pandoc.AlignLeft, 0.72},
  }
  return element
end
