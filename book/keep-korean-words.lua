-- Keep each whitespace-delimited Korean/CJK word on one PDF line.
-- Pandoc represents whitespace-separated words as Str nodes, so this does
-- not guess morphology or rewrite prose. Code nodes are not affected.

local function contains_korean_or_hanja(text)
  for _, codepoint in utf8.codes(text) do
    if (codepoint >= 0x1100 and codepoint <= 0x11FF)
      or (codepoint >= 0x3130 and codepoint <= 0x318F)
      or (codepoint >= 0xA960 and codepoint <= 0xA97F)
      or (codepoint >= 0xAC00 and codepoint <= 0xD7A3)
      or (codepoint >= 0xD7B0 and codepoint <= 0xD7FF)
      or (codepoint >= 0x3400 and codepoint <= 0x4DBF)
      or (codepoint >= 0x4E00 and codepoint <= 0x9FFF)
      or (codepoint >= 0xF900 and codepoint <= 0xFAFF)
      or (codepoint >= 0x20000 and codepoint <= 0x2FA1F) then
      return true
    end
  end
  return false
end

function Str(element)
  if FORMAT:match("latex") and contains_korean_or_hanja(element.text) then
    return {
      pandoc.RawInline("latex", "\\keepkoreanword{"),
      element,
      pandoc.RawInline("latex", "}"),
    }
  end
end
