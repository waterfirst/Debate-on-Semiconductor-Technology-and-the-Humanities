-- Keep a formal Korean sentence ending with the word immediately before it.
-- This prevents a final "합니다." or "합니까?" from sitting alone on a PDF
-- line. The prose is not rewritten, and non-LaTeX formats are unchanged.

local function trim_sentence_marks(text)
  return text:gsub('[%.%!%?…]+$', '')
end

local function is_formal_sentence_ending(text)
  local stem = trim_sentence_marks(text)
  return stem:sub(-6) == '니다' or stem:sub(-6) == '니까'
end

local function bind_final_ending(block)
  if not FORMAT:match('latex') then
    return nil
  end

  local content = block.content
  local last_str = nil
  for i = #content, 1, -1 do
    if content[i].t == 'Str' then
      last_str = i
      break
    elseif content[i].t ~= 'Note' then
      return nil
    end
  end

  if not last_str or not is_formal_sentence_ending(content[last_str].text) then
    return nil
  end

  for i = last_str - 1, 1, -1 do
    if content[i].t == 'Space' then
      content[i] = pandoc.RawInline('latex', '~')
      return block
    elseif content[i].t ~= 'Note' then
      return nil
    end
  end
end

function Para(block)
  return bind_final_ending(block)
end

function Plain(block)
  return bind_final_ending(block)
end
