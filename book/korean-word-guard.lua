-- Prevent Korean words from leaving a single final syllable on the next line/page.
-- For short eojeol, keep the whole Hangul run together. For longer ones, keep
-- the final three syllables together. HTML/EPUB output remains unchanged.

if not FORMAT:match("latex") then
  return {}
end

local trailing_punctuation = {
  [0x2E] = true, [0x2C] = true, [0x21] = true, [0x3F] = true,
  [0x3A] = true, [0x3B] = true, [0x22] = true, [0x27] = true,
  [0x29] = true, [0x5D] = true,
  [0x3002] = true, [0x300D] = true, [0x300F] = true,
  [0x2019] = true, [0x201D] = true,
}

local function is_hangul(codepoint)
  return codepoint >= 0xAC00 and codepoint <= 0xD7A3
end

function Str(element)
  local chars = {}
  for position, codepoint in utf8.codes(element.text) do
    chars[#chars + 1] = { position = position, codepoint = codepoint }
  end
  if #chars < 3 then
    return nil
  end

  local run_end = #chars
  while run_end > 0 and trailing_punctuation[chars[run_end].codepoint] do
    run_end = run_end - 1
  end
  if run_end == 0 or not is_hangul(chars[run_end].codepoint) then
    return nil
  end

  local run_start = run_end
  while run_start > 1 and is_hangul(chars[run_start - 1].codepoint) do
    run_start = run_start - 1
  end
  local run_length = run_end - run_start + 1
  if run_length < 2 then
    return nil
  end

  local guard_start = run_start
  if run_length > 5 then
    guard_start = run_end - 2
  end
  local byte_start = chars[guard_start].position
  local prefix = element.text:sub(1, byte_start - 1)
  local suffix = element.text:sub(byte_start)
  local guarded = pandoc.RawInline("latex", "\\mbox{" .. suffix .. "}")
  if prefix == "" then
    return guarded
  end
  return { pandoc.Str(prefix), guarded }
end
