# 312_bot - Discord Bot with Roblox Integration

A Discord bot integrated with an Express.js API server for managing Roblox user bans and item restorations. The bot provides slash commands for moderation and saves announcements to Google Sheets.

## Features

- **Discord Moderation**: Ban users on Discord with DM notifications and appeal links
- **Roblox Ban Management**: Ban/unban Roblox users with support for temporary bans (durations like 30s, 1m, 5h, 10d, 2y)
- **Ban List Management**: View paginated lists of banned users with expiration details
- **Item Restoration**: Queue items for restoration when banned users return to Roblox games
- **Announcement Monitoring**: Automatically saves messages from a specific Discord channel to Google Sheets
- **REST API**: Express.js server providing endpoints for ban management and restoration queue
- **Local Storage**: Uses JSON files for persistent storage of ban lists and restoration queues

## Setup

### Prerequisites

- Node.js (for API server)
- Python 3.8+ (for Discord bot)
- Google Cloud Project with Sheets API enabled
- Discord Bot Token

## API Endpoints

The Express.js server provides REST endpoints for ban management and item restoration.

### Ban Management

#### `POST /ban`
Ban a Roblox user.

**Request Body:**
```json
{
  "platform": "roblox",
  "username": "string",
  "reason": "string",
  "duration": "string" // optional, e.g., "30s", "1m", "5h", "10d", "2y"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Roblox user username has been banned",
  "banEntry": {...},
  "bannedUsers": [...]
}
```

#### `POST /unban`
Unban a Roblox user.

**Request Body:**
```json
{
  "platform": "roblox",
  "username": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Roblox user username has been unbanned",
  "removedBan": {...},
  "bannedUsers": [...]
}
```

#### `GET /banlist?platform=roblox`
Get the list of banned Roblox users.

**Response:**
```json
{
  "success": true,
  "bannedUsers": [...],
  "count": 5
}
```

### Item Restoration

#### `POST /restore`
Queue items for restoration when a user returns to the game.

**Request Body:**
```json
{
  "username": "string",
  "items": "string" // or ["string1", "string2"]
}
```

**Response:**
```json
{
  "success": true,
  "message": "Restoration queue updated for user username",
  "restorationQueue": [...]
}
```

#### `GET /restorationqueue`
Get the current restoration queue.

**Response:**
```json
{
  "success": true,
  "queue": [...],
  "count": 3
}
```

#### `POST /restore/confirm`
Confirm that restoration has been completed (called by Roblox scripts).

**Request Body:**
```json
{
  "username": "string"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Restoration confirmed and queue cleared for user username"
}
```

### Health Check

#### `GET /health`
Check if the API server is running.

**Response:**
```json
{
  "status": "OK",
  "message": "API server is running"
}
```

## Discord Commands

The bot provides slash commands for moderation and restoration management.

### `/ban`
Ban a user on Discord or Roblox.

**Parameters:**
- `platform`: discord or roblox
- `discord_user`: Discord user to ban (required for Discord bans)
- `roblox_username`: Roblox username to ban (required for Roblox bans)
- `reason`: Reason for the ban (optional)
- `duration`: Ban duration (optional, only for Roblox, e.g., "30s", "1m", "5h", "10d", "2y")

**Permissions:** Administrator or specific roles

### `/unban`
Unban a Roblox user.

**Parameters:**
- `roblox_username`: Roblox username to unban

**Permissions:** Administrator or specific roles

### `/getbanlist`
Get the list of banned Roblox users with pagination.

**Permissions:** Administrator or specific roles

### `/restore`
Queue items for restoration when a user returns to the Roblox game.

**Parameters:**
- `username`: Roblox username
- `items`: Comma-separated list of items to restore

**Permissions:** Administrator or specific roles

### `/restorerequests`
Get the list of pending restoration requests with pagination.

**Permissions:** Administrator or specific roles

**Example Roblox Server Script:**
```lua
local HttpService = game:GetService("HttpService")
local Players = game:GetService("Players")

local API_URL = "http://your-server-ip:3000"

local function checkBans()
    local success, response = pcall(function()
        return HttpService:GetAsync(API_URL .. "/banlist?platform=roblox")
    end)

    if success then
        local data = HttpService:JSONDecode(response)
        if data.success and data.bannedUsers then
            for _, player in ipairs(Players:GetPlayers()) do
                for _, banEntry in ipairs(data.bannedUsers) do
                    if player.UserId == banEntry.userId then
                        player:Kick("You have been banned from this game. Reason: " .. (banEntry.reason or "No reason provided"))
                        break
                    end
                end
            end
        end
    end
end

local function checkRestorations()
    local success, response = pcall(function()
        return HttpService:GetAsync(API_URL .. "/restorationqueue")
    end)

    if success then
        local data = HttpService:JSONDecode(response)
        if data.success and data.queue then
            for _, player in ipairs(Players:GetPlayers()) do
                for _, entry in ipairs(data.queue) do
                    if string.lower(player.Name) == string.lower(entry.username) then
                        -- Restore items for the player
                        -- Add your restoration logic here

                        -- Confirm restoration
                        local confirmSuccess, confirmResponse = pcall(function()
                            return HttpService:PostAsync(API_URL .. "/restore/confirm", HttpService:JSONEncode({username = entry.username}), Enum.HttpContentType.ApplicationJson)
                        end)
                        break
                    end
                end
            end
        end
    end
end

while true do
    checkBans()
    checkRestorations()
    wait(5) -- Check every 5 seconds
end
```

## File Structure

```
312_bot/
├── bot.py                 # Discord bot main file
├── request.js             # Express.js API server
├── package.json           # Node.js dependencies
├── requirements.txt       # Python dependencies
├── README.md              # This file
├── .env                   # Environment variables
├── ban_list.json          # Local ban list storage
├── restoration_queue.json # Local restoration queue storage
├── ski1111-d82ba6b3cf0a.json # Google service account credentials
└── .gitignore
```

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DISCORD_TOKEN` | Discord bot token | Yes |
| `GUILD_ID` | Discord server ID | Yes |
| `GOOGLE_SHEETS_CREDENTIALS` | Path to Google service account JSON file OR JSON string containing credentials | Yes |
| `SPREADSHEET_ID` | Google Sheets spreadsheet ID | Yes |
| `API_SERVER_URL` | URL of the API server | No (defaults to http://localhost:3000) |
| `PORT` | Port for the API server | No (defaults to 3000) |

## Permissions

The bot requires specific Discord permissions and role IDs for ban commands. Update the `allowed_role_ids` in `bot.py` to match your server's moderator roles.