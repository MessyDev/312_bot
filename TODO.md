# TODO for Enhanced Ban System Implementation

- [x] Remove Roblox API dependencies from request.js
- [x] Implement local ban list storage using JSON file
- [x] Update POST /ban endpoint to add users to local ban list with duration support
- [x] Update GET /banlist endpoint to return local ban list with full ban details
- [x] Add POST /unban endpoint to remove users from ban list
- [x] Implement automatic ban expiration in API server
- [x] Update Discord bot ban command to accept duration parameter
- [x] Add unban command to Discord bot
- [x] Add getbanlist command with pagination (10 per page, left/right buttons)
- [x] Create Roblox script to poll GET /banlist every second and kick banned users
- [ ] User to install Node.js dependencies: `npm install`
- [ ] User to run API server: `npm start` or `npm run dev`
- [ ] User to set environment variable `API_SERVER_URL` to point to the API server URL (default http://localhost:3000)
- [ ] User to test ban commands on Discord for Roblox platform with duration
- [ ] User to test unban command and getbanlist command with pagination
- [ ] User to implement Roblox script in their Roblox game (replace API_URL with actual server IP)
- [ ] User to test end-to-end ban system including automatic expiration
- [ ] Optionally extend request.js to support Discord ban APIs if needed
- [ ] Document usage and setup instructions in README.md

## New Features Implemented

### Ban Duration Support
- Ban commands now accept duration in format: 30s, 1m, 5h, 10d, 2y
- Automatic expiration handled by API server
- Ban list stored with expiration timestamps

### Unban Command
- `/unban roblox_username:<username>` - Removes user from ban list
- Updates both API server and local JSON file

### Get Ban List with Pagination
- `/getbanlist` - Shows banned users with pagination
- 10 users per page with left/right navigation buttons
- Shows username, reason, duration, and expiration time

### Roblox Script
- Polls API server every second for ban list updates
- Automatically kicks banned players
- Handles both new joins and existing players

## Environment Variables

Required in .env:
- `API_SERVER_URL`: URL of the API server (default: http://localhost:3000)

## Testing Steps

1. Install dependencies: `npm install`
2. Start API server: `npm start`
3. Start Discord bot: `python bot.py`
4. Test ban with duration: `/ban platform:roblox roblox_username:testuser duration:5m reason:Testing`
5. Test getbanlist: `/getbanlist`
6. Test unban: `/unban roblox_username:testuser`
7. Implement Roblox script in your game and test real-time banning
8. Test automatic expiration by setting short duration and waiting
