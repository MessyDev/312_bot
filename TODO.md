# TODO for Local Ban List Management

- [x] Remove Roblox API dependencies from request.js
- [x] Implement local ban list storage using JSON file
- [x] Update POST /ban endpoint to add users to local ban list
- [x] Update GET /banlist endpoint to return local ban list
- [x] Keep user ID lookup functionality for username to ID conversion
- [ ] User to start API server: `npm start`
- [ ] User to test ban commands from Discord bot
- [ ] User to implement Roblox script to poll GET /banlist every second
- [ ] User to test end-to-end ban system

## Roblox Script Implementation

The Roblox script should:
1. Poll `GET /banlist?platform=roblox` every second
2. Check if any player UserIds are in the banned list
3. Kick/ban players who are in the banned list

Example Roblox script structure:
```lua
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

local API_URL = "http://your-server-ip:3000/banlist?platform=roblox"

local function checkBanList()
    local success, response = pcall(function()
        return HttpService:GetAsync(API_URL)
    end)

    if success then
        local data = HttpService:JSONDecode(response)
        if data.success and data.bannedUsers then
            -- Check current players against ban list
            for _, player in ipairs(Players:GetPlayers()) do
                if table.find(data.bannedUsers, player.UserId) then
                    player:Kick("You have been banned from this game.")
                end
            end
        end
    end
end

-- Poll every second
while true do
    checkBanList()
    wait(1)
end
```

## Environment Variables

Required in .env:
- `API_SERVER_URL`: URL of the API server (default: http://localhost:3000)

## Testing

1. Start API server: `npm start`
2. Start Discord bot: `python bot.py`
3. Use `/ban platform:roblox roblox_username:testuser` in Discord
4. Check that ban_list.json is created/updated
5. Test GET /banlist endpoint returns the banned user
