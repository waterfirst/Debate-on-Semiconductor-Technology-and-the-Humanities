-- Give evidence tables practical widths on the narrow A5 page.

local function header_text(cell)
  return pandoc.utils.stringify(cell.contents or cell)
end

local function apply_widths(tbl, widths)
  for index, width in ipairs(widths) do
    local alignment = tbl.colspecs[index][1]
    tbl.colspecs[index] = { alignment, width }
  end
end

function Table(tbl)
  local rows = tbl.head and tbl.head.rows or {}
  if #rows == 0 or #rows[1].cells == 0 then
    return tbl
  end
  local first = header_text(rows[1].cells[1]):gsub("%s+", "")
  local columns = #tbl.colspecs

  if columns == 4 and (first == "근거" or first == "구분") then
    -- The classification column needs enough room for terms such as
    -- "조건부 전망"; the prior 16% column wrapped almost every word.
    apply_widths(tbl, { 0.10, 0.32, 0.22, 0.36 })
  elseif columns == 4 and first == "단계" then
    -- Control-ladder tables have one short ordinal and three prose columns.
    -- Giving equal quarters to all four columns wastes A5 width on the ordinal
    -- and forces Korean terms in the evidence columns to break character by character.
    apply_widths(tbl, { 0.09, 0.29, 0.30, 0.32 })
  elseif columns == 3 and (first == "근거" or first == "구분") then
    apply_widths(tbl, { 0.10, 0.51, 0.39 })
  elseif columns == 3 and (first == "우선순위" or first == "순서") then
    -- Data-acquisition tables use a short ordinal, a compact source name,
    -- and a substantially longer verification checklist.  Equal columns
    -- make the checklist wrap into four or five lines on the A5 page.
    apply_widths(tbl, { 0.13, 0.34, 0.53 })
  elseif columns == 2 and (first == "판정축" or first == "항목") then
    apply_widths(tbl, { 0.30, 0.70 })
  end
  return tbl
end
