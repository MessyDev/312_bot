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
    const { platform, username, reason = 'No reason provided' } = req.body;

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
            if (!bannedUsers.includes(userId)) {
                bannedUsers.push(userId);
                saveBanList(bannedUsers);
                console.log(`Banned Roblox user ${username} (ID: ${userId}) for reason: ${reason}`);
            } else {
                console.log(`User ${username} (ID: ${userId}) is already banned`);
            }

            res.json({
                success: true,
                message: `Roblox user ${username} has been banned`,
                userId,
                reason,
                bannedUsers: bannedUsers
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

// Health check endpoint
app.get('/health', (req, res) => {
    res.json({ status: 'OK', message: 'API server is running' });
});

app.listen(PORT, () => {
    console.log(`API server running on port ${PORT}`);
});
