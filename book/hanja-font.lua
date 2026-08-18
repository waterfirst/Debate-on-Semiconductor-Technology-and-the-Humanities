-- Route every CJK ideograph and CJK punctuation mark to the dedicated font.
-- This includes source quotations inside footnotes, not only explicit .hanja spans.
local function is_cjk(codepoint)
  return (codepoint >= 0x3000 and codepoint <= 0x303F)
      or (codepoint >= 0x3400 and codepoint <= 0x4DBF)
      or (codepoint >= 0x4E00 and codepoint <= 0x9FFF)
      or (codepoint >= 0xF900 and codepoint <= 0xFAFF)
      or (codepoint >= 0x20000 and codepoint <= 0x2FA1F)
end

function Str(el)
  if not FORMAT:match("latex") then
    return nil
  end

  local chunks = {}
  local buffer = ""
  local buffer_is_cjk = nil

  local function flush()
    if buffer == "" then
      return
    end
    if buffer_is_cjk then
      table.insert(chunks, pandoc.RawInline("latex", "{\\HanjaFont " .. buffer .. "}"))
    else
      table.insert(chunks, pandoc.Str(buffer))
    end
    buffer = ""
  end

  for _, codepoint in utf8.codes(el.text) do
    local char_is_cjk = is_cjk(codepoint)
    if buffer_is_cjk ~= nil and char_is_cjk ~= buffer_is_cjk then
      flush()
    end
    buffer_is_cjk = char_is_cjk
    buffer = buffer .. utf8.char(codepoint)
  end
  flush()

  if #chunks == 1 and not buffer_is_cjk then
    return nil
  end
  return chunks
end
