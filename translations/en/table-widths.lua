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
  local first = header_text(rows[1].cells[1]):lower():gsub("%s+", " ")
  local columns = #tbl.colspecs

  if columns == 4 and (first == "evidence" or first == "category") then
    apply_widths(tbl, { 0.10, 0.32, 0.22, 0.36 })
  elseif columns == 4 and first == "step" then
    apply_widths(tbl, { 0.09, 0.29, 0.30, 0.32 })
  elseif columns == 3 and (first == "evidence" or first == "category") then
    apply_widths(tbl, { 0.10, 0.51, 0.39 })
  elseif columns == 3 and (first == "priority" or first == "order") then
    apply_widths(tbl, { 0.13, 0.34, 0.53 })
  elseif columns == 2 and (first == "decision axis" or first == "item") then
    apply_widths(tbl, { 0.30, 0.70 })
  end
  return tbl
end
