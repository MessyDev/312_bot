-- Roblox Ban System Script
-- This script polls the API server every second to check for banned users
-- Place this in a ServerScript in ServerScriptService

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- Configuration
local API_URL = "http://your-server-ip:3000/banlist?platform=roblox"  -- Replace with your API server URL
local POLL_INTERVAL = 1  -- Poll every 1 second

-- Cache for banned user IDs (for faster lookup)
local bannedUserIds = {}

-- Function to update ban list from API
local function updateBanList()
    local success, response = pcall(function()
        return HttpService:GetAsync(API_URL)
    end)

    if success then
        local success2, data = pcall(function()
            return HttpService:JSONDecode(response)
        end)

        if success2 and data.success and data.bannedUsers then
            -- Clear current cache
            bannedUserIds = {}

            -- Update cache with current banned users
            for _, banEntry in ipairs(data.bannedUsers) do
                bannedUserIds[banEntry.userId] = true
            end

            print("Updated ban list. Total banned users: " .. #data.bannedUsers)
        else
            warn("Failed to parse ban list response")
        end
    else
        warn("Failed to fetch ban list from API: " .. tostring(response))
    end
end

-- Function to check and kick banned players
local function checkAndKickPlayers()
    for _, player in ipairs(Players:GetPlayers()) do
        if bannedUserIds[player.UserId] then
            -- Player is banned, kick them
            player:Kick("You have been banned from this game.")
            print("Kicked banned player: " .. player.Name .. " (ID: " .. player.UserId .. ")")
        end
    end
end

-- Function to handle new player joins
local function onPlayerAdded(player)
    -- Small delay to ensure ban list is loaded
    wait(0.1)

    if bannedUserIds[player.UserId] then
        player:Kick("You have been banned from this game.")
        print("Kicked banned player on join: " .. player.Name .. " (ID: " .. player.UserId .. ")")
    end
end

-- Connect player join event
Players.PlayerAdded:Connect(onPlayerAdded)

-- Main polling loop
while true do
    updateBanList()
    checkAndKickPlayers()
    wait(POLL_INTERVAL)
end
