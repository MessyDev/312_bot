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

- `/ban platform:<discord|roblox> discord_user:@user roblox_username:<username> reason:<reason>`

### Discord Ban

- Sends a DM to the user with a ban message, reason, and an appeal link: https://appealexample.com
- Bans the user from the Discord server.

### Roblox Ban

- Placeholder implementation to ban a user on Roblox.
- You need to set up your Roblox game's ban system and provide API credentials.

### Setup for Roblox Ban System

1. **Create or use a Roblox game**: The bot is configured for game ID 122343477195976 (Universe ID: 8709300312). If using your own game, update the code accordingly.
2. **Find your Universe ID**: Go to your Roblox game page, the Universe ID is in the URL or can be found via Roblox API. For example, use https://apis.roblox.com/universes/v1/places/122343477195976/universe to get the universe ID.
3. **Set up Roblox Open Cloud API**:
   - Go to [Roblox Creator Dashboard](https://create.roblox.com/dashboard).
   - Select your experience (game).
   - Go to Game Settings > Security > API Keys.
   - Click "Create API Key".
   - Name it (e.g., "Ban System API").
   - Select scopes: Enable "DataStore" (Read/Write).
   - Set restrictions: You can limit to specific DataStore names if desired (e.g., "BannedUsers").
   - Click "Create API Key" and copy the generated key.
4. **Implement ban checking in your Roblox game**:
   - In your game's server script, check the "BannedUsers" DataStore entry "BannedList" on player join.
   - If the player's UserId is in the list, kick or ban them.
5. **Set environment variables in your `.env` file**:
   - `ROBLOX_API_KEY`: Your Roblox Open Cloud API key.
   - `ROBLOX_UNIVERSE_ID`: Your Roblox game universe ID.
6. The bot will automatically add banned users to the DataStore when using the /ban command.

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
