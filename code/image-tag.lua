--[[
  Automatically convert an image filename into a HTML image tag.
--]]

-- http://stackoverflow.com/questions/132397/get-back-the-output-of-os-execute-in-lua
function os.capture(cmd, raw)
  local f = assert(io.popen(cmd, 'r'))
  local s = assert(f:read('*a'))
  f:close()
  if raw then return s end
  s = string.gsub(s, '^%s+', '')
  s = string.gsub(s, '%s+$', '')
  s = string.gsub(s, '[\n\r]+', ' ')
  return s
end

local window = 100
local str
local sel = true
local start, stop = geany.select()
if start == stop then
    sel = false
    -- Select the current word.  For some reason, geany.find() raises
    -- segmentation faults, so do it the hard way.
    geany.select(start-window, start)
    str = geany.selection()
    a,b = string.find(str, '%S*$')
    start = start - b + a - 1 -- b will be window, unless we hit the first char
    geany.select(start, start+window)
    str = geany.selection()
    a,b = string.find(str, '^%S*')
    geany.select(start, start+b)
end
fn = geany.selection()

str = os.capture("identify -format 'height=\"%h\" width=\"%w\"' "..geany.dirname(geany.filename())..geany.dirsep..fn)
if str=='' then 
    if not sel then
        geany.select(stop,stop)
    end
    geany.message("Error", "Could not find image file: "..fn)
    return
end

geany.selection('<img src="'..fn..'" '..str..' alt="" />')

