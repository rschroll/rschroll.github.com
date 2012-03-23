--[[
  Open tab in new window, by closing the current tab and starting a new
  instance of geany.
--]]

local filename = geany.filename()
if filename ~= nil then
    if geany.close() then
        geany.launch("geany", "-i", filename)
    end
end
