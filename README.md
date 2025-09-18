# Discord Bot - 312_bot

A Discord bot that saves messages from the 'announcements' channel to Google Sheets.

## Setup

1. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Set up Google Sheets:
   - Create a Google Cloud Project
   - Enable Google Sheets API
   - Create a Service Account and download the JSON credentials file
   - Place the credentials.json file in the project root
   - Create a Google Sheet and share it with the service account email
   - Copy the Spreadsheet ID from the URL and update .env

3. Update .env with your credentials:
   - DISCORD_TOKEN: Your Discord bot token
   - GOOGLE_SHEETS_CREDENTIALS: Path to credentials.json (default: credentials.json)
   - SPREADSHEET_ID: Your Google Sheet ID

4. Run the bot:
   ```
   python bot.py
   ```

## Features

- Monitors the 'announcements' channel
- Saves each message content as a string to Google Sheets

## Ban Command Feature

This bot now includes a `/ban` slash command to ban users on Discord or Roblox.

### Usage

- `/ban platform:<discord|roblox> discord_user:@user roblox_username:<username> reason:<reason> duration:<duration>`
- `/unban roblox_username:<username>`
- `/getbanlist`

### Discord Ban

- Sends a DM to the user with a ban message, reason, and an appeal link: https://appealexample.com
- Bans the user from the Discord server.

### Roblox Ban

- Bans users locally by storing their User IDs in a JSON file with ban details.
- Supports ban duration (e.g., 30s, 1m, 5h, 10d, 2y) with automatic expiration.
- The API server maintains the ban list and provides it to Roblox scripts.
- Roblox scripts poll the API server every second to check for banned users.
- Includes unban functionality and paginated ban list viewing.

### Setup for Local Roblox Ban System

1. **Start the API server**:
   ```bash
   npm install
   npm start
   ```

2. **Implement ban checking in your Roblox game**:
   - Add a server script that polls the API server every second
   - Check if any current players' UserIds are in the banned list
   - Kick players who are banned

3. **Example Roblox server script**:
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
               for _, player in ipairs(Players:GetPlayers()) do
                   if table.find(data.bannedUsers, player.UserId) then
                       player:Kick("You have been banned from this game.")
                   end
               end
           end
       end
   end

   while true do
       checkBanList()
       wait(1)
   end
   ```

4. **Set environment variables in your `.env` file**:
   - `API_SERVER_URL`: URL of your API server (default: http://localhost:3000)

5. The bot will add banned users to the local ban list when using the /ban command.

### Environment Variables

- `DISCORD_TOKEN`: Your Discord bot token.
- `GOOGLE_SHEETS_CREDENTIALS`: Path to your Google service account JSON.
- `SPREADSHEET_ID`: Your Google Sheets spreadsheet ID.
- `ROBLOX_API_KEY`: Your Roblox API key (for ban system).
- `ROBLOX_UNIVERSE_ID`: Your Roblox game universe ID.

### Running the Bot

```bash
pip install -r requirements.txt
python bot.py
```
