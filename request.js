const express = require('express');
const axios = require('axios');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Local storage for ban list
const BAN_LIST_FILE = path.join(__dirname, 'ban_list.json');

// Helper function to load ban list from file
function loadBanList() {
    try {
        if (fs.existsSync(BAN_LIST_FILE)) {
            const data = fs.readFileSync(BAN_LIST_FILE, 'utf8');
            return JSON.parse(data);
        }
    } catch (error) {
        console.error('Error loading ban list:', error);
    }
    return [];
}

// Helper function to save ban list to file
function saveBanList(banList) {
    try {
        fs.writeFileSync(BAN_LIST_FILE, JSON.stringify(banList, null, 2));
    } catch (error) {
        console.error('Error saving ban list:', error);
    }
}

// Initialize ban list
let bannedUsers = loadBanList();

// Helper function to parse duration string (e.g., "30s", "1m", "5h", "10d", "2y")
function parseDuration(durationStr) {
    if (!durationStr) return null;

    const match = durationStr.match(/^(\d+)([smhdy])$/);
    if (!match) return null;

    const value = parseInt(match[1]);
    const unit = match[2];

    let seconds = 0;
    switch (unit) {
        case 's': seconds = value; break;
        case 'm': seconds = value * 60; break;
        case 'h': seconds = value * 3600; break;
        case 'd': seconds = value * 86400; break;
        case 'y': seconds = value * 31536000; break; // 365 days
    }

    return seconds;
}

// Helper function to clean expired bans
function cleanExpiredBans() {
    const now = Date.now();
    const originalLength = bannedUsers.length;

    bannedUsers = bannedUsers.filter(ban => {
        if (ban.expiresAt && ban.expiresAt <= now) {
            console.log(`Ban expired for user ID: ${ban.userId}`);
            return false;
        }
        return true;
    });

    if (bannedUsers.length !== originalLength) {
        saveBanList(bannedUsers);
    }
}

// Clean expired bans on startup and every minute
setInterval(cleanExpiredBans, 60000);
cleanExpiredBans();

// Helper function to get Roblox user ID from username
async function getRobloxUserId(username) {
    try {
        const response = await axios.post('https://users.roblox.com/v1/usernames/users', {
            usernames: [username]
        });
        if (response.data.data && response.data.data.length > 0) {
            return response.data.data[0].id;
        }
    } catch (error) {
        console.error('Error getting Roblox user ID:', error.message);
    }
    return null;
}

// POST endpoint for banning users
app.post('/ban', async (req, res) => {
    console.log('Ban request received:', req.body);
    const { platform, username, reason = 'No reason provided', duration } = req.body;

    if (!platform || !username) {
        console.log('Missing platform or username');
        return res.status(400).json({ error: 'Platform and username are required' });
    }

    if (platform === 'roblox') {
        console.log('Getting user ID for username:', username);
        const userId = await getRobloxUserId(username);
        console.log('User ID result:', userId);

        if (!userId) {
            console.log('User not found');
            return res.status(404).json({ error: 'Roblox user not found' });
        }

        try {
            // Check if user is already banned
            const existingBan = bannedUsers.find(ban => ban.userId === userId);
            if (existingBan) {
                console.log(`User ${username} (ID: ${userId}) is already banned`);
                return res.status(409).json({ error: 'User is already banned' });
            }

            // Parse duration if provided
            let expiresAt = null;
            if (duration) {
                const durationSeconds = parseDuration(duration);
                if (durationSeconds) {
                    expiresAt = Date.now() + (durationSeconds * 1000);
                } else {
                    return res.status(400).json({ error: 'Invalid duration format. Use format like: 30s, 1m, 5h, 10d, 2y' });
                }
            }

            const banEntry = {
                userId: userId,
                username: username,
                reason: reason,
                bannedAt: Date.now(),
                expiresAt: expiresAt,
                duration: duration || null
            };

            bannedUsers.push(banEntry);
            saveBanList(bannedUsers);
            console.log(`Banned Roblox user ${username} (ID: ${userId}) for reason: ${reason}${duration ? `, duration: ${duration}` : ''}`);

            res.json({
                success: true,
                message: `Roblox user ${username} has been banned${duration ? ` for ${duration}` : ''}`,
                banEntry: banEntry,
                bannedUsers: bannedUsers.map(ban => ban.userId) // Return just userIds for compatibility
            });
        } catch (error) {
            console.error('Error banning Roblox user:', error.message);
            res.status(500).json({ error: 'Failed to ban Roblox user' });
        }
    } else {
        res.status(400).json({ error: 'Unsupported platform. Only "roblox" is supported for now.' });
    }
});

// GET endpoint for retrieving ban list
app.get('/banlist', (req, res) => {
    const { platform } = req.query;

    if (!platform) {
        return res.status(400).json({ error: 'Platform is required' });
    }

    if (platform === 'roblox') {
        console.log('Returning ban list:', bannedUsers);
        res.json({
            success: true,
            bannedUsers: bannedUsers,
            count: bannedUsers.length
        });
    } else {
        res.status(400).json({ error: 'Unsupported platform. Only "roblox" is supported for now.' });
    }
});

// POST endpoint for unbanning users
app.post('/unban', async (req, res) => {
    console.log('Unban request received:', req.body);
    const { platform, username } = req.body;

    if (!platform || !username) {
        console.log('Missing platform or username');
        return res.status(400).json({ error: 'Platform and username are required' });
    }

    if (platform === 'roblox') {
        console.log('Getting user ID for username:', username);
        const userId = await getRobloxUserId(username);
        console.log('User ID result:', userId);

        if (!userId) {
            console.log('User not found');
            return res.status(404).json({ error: 'Roblox user not found' });
        }

        try {
            // Find and remove the ban
            const banIndex = bannedUsers.findIndex(ban => ban.userId === userId);
            if (banIndex === -1) {
                console.log(`User ${username} (ID: ${userId}) is not banned`);
                return res.status(404).json({ error: 'User is not banned' });
            }

            const removedBan = bannedUsers.splice(banIndex, 1)[0];
            saveBanList(bannedUsers);
            console.log(`Unbanned Roblox user ${username} (ID: ${userId})`);

            res.json({
                success: true,
                message: `Roblox user ${username} has been unbanned`,
                removedBan: removedBan,
                bannedUsers: bannedUsers.map(ban => ban.userId) // Return just userIds for compatibility
            });
        } catch (error) {
            console.error('Error unbanning Roblox user:', error.message);
            res.status(500).json({ error: 'Failed to unban Roblox user' });
        }
    } else {
        res.status(400).json({ error: 'Unsupported platform. Only "roblox" is supported for now.' });
    }
});

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'OK', message: 'API server is running' });
});

app.listen(PORT, () => {
    console.log(`API server running on port ${PORT}`);
});
