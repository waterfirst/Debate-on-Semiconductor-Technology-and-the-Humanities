-- 전자책만 컬러 그림을 쓰게 한다.
--
-- 본문 .qmd 는 figures/*-print.png 를 참조한다. POD 종이책이 흑백 인쇄라
-- 그렇게 맞춰 둔 것인데, EPUB 이 그 파이프라인을 그대로 물려받아 2026-09-01
-- 빌드의 이미지 39개 중 38개가 흑백으로 들어갔다(2026-09-12 확인).
--
-- 참조 60곳을 고치면 종이책이 깨지므로 출력 형식에 따라 경로만 바꾼다.
-- 컬러 원본이 없으면 -print 를 그대로 둔다. 그림이 사라지는 것보다 낫다.

local function color_variant(src)
  local base = src:match("^(.*)%-print(%.[%a]+)$")
  if not base then return nil end
  return base .. src:match("(%.[%a]+)$")
end

local function exists(path)
  local f = io.open(path, "r")
  if f then f:close(); return true end
  return false
end

function Image(el)
  if not (FORMAT:match("epub")) then return nil end
  local alt = color_variant(el.src)
  if not alt then return nil end
  -- .qmd 는 chapters/ 에서 ../figures/... 로 참조한다. 실제 파일은 book/figures/ 다.
  local probe = alt:gsub("^%.%./", "")
  if exists(probe) or exists(alt) then
    el.src = alt
    return el
  end
  io.stderr:write("epub-color-figures: 컬러 원본 없음, -print 유지 → " .. el.src .. "\n")
  return nil
end
