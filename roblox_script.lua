-- Roblox Ban System & Item Restoration Script
-- This script polls the API server every second to check for banned users and restoration queue
-- Place this in a ServerScript in ServerScriptService

local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

-- Configuration
local API_URL = "http://your-server-ip:3000"  -- Replace with your API server URL
local POLL_INTERVAL = 1  -- Poll every 1 second

-- Cache for banned user IDs (for faster lookup)
local bannedUserIds = {}

-- Cache for restoration queue (username -> items)
local restorationQueue = {}

-- Function to update ban list from API
local function updateBanList()
    local success, response = pcall(function()
        return HttpService:GetAsync(API_URL .. "/banlist?platform=roblox")
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

-- Function to update restoration queue from API
local function updateRestorationQueue()
    local success, response = pcall(function()
        return HttpService:GetAsync(API_URL .. "/restorationqueue")
    end)

    if success then
        local success2, data = pcall(function()
            return HttpService:JSONDecode(response)
        end)

        if success2 and data.success and data.queue then
            -- Update restoration queue
            restorationQueue = {}
            for _, entry in ipairs(data.queue) do
                restorationQueue[entry.username:lower()] = entry.items
            end

            print("Updated restoration queue. Total entries: " .. #data.queue)
        else
            warn("Failed to parse restoration queue response")
        end
    else
        warn("Failed to fetch restoration queue from API: " .. tostring(response))
    end
end

-- Function to restore items for a player
local function restorePlayerItems(player, items)
    print("Restoring items for player: " .. player.Name)

    -- This is where you would implement your item restoration logic
    -- For example, giving items to the player's inventory, backpack, etc.

    -- Example restoration logic (customize based on your game's item system):
    for _, itemName in ipairs(items) do
        print("Restoring item: " .. itemName .. " to player: " .. player.Name)

        -- Add your item restoration code here
        -- For example:
        -- local item = game.ServerStorage.Items[itemName]:Clone()
        -- item.Parent = player.Backpack
        -- or
        -- player.leaderstats.Coins.Value = player.leaderstats.Coins.Value + itemValue
    end

    -- Send confirmation to API server
    local success, response = pcall(function()
        local payload = HttpService:JSONEncode({
            username = player.Name
        })

        return HttpService:PostAsync(API_URL .. "/restore/confirm", payload, Enum.HttpContentType.ApplicationJson)
    end)

    if success then
        print("Restoration confirmed for player: " .. player.Name)
    else
        warn("Failed to confirm restoration for player: " .. player.Name .. " - " .. tostring(response))
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
    -- Small delay to ensure data is loaded
    wait(0.1)

    -- Check if player is banned
    if bannedUserIds[player.UserId] then
        player:Kick("You have been banned from this game.")
        print("Kicked banned player on join: " .. player.Name .. " (ID: " .. player.UserId .. ")")
        return
    end

    -- Check if player has items to restore
    local playerItems = restorationQueue[player.Name:lower()]
    if playerItems then
        print("Player has items to restore: " .. player.Name)
        restorePlayerItems(player, playerItems)
    end
end

-- Connect player join event
Players.PlayerAdded:Connect(onPlayerAdded)

-- Main polling loop
while true do
    updateBanList()
    updateRestorationQueue()
    checkAndKickPlayers()
    wait(POLL_INTERVAL)
end
