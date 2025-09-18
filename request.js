const express = require('express');
const axios = require('axios');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(express.json());

// Environment variables
const ROBLOX_API_KEY = process.env.ROBLOX_API_KEY;
const ROBLOX_UNIVERSE_ID = process.env.ROBLOX_UNIVERSE_ID;

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
    const { platform, username, reason = 'No reason provided' } = req.body;

    if (!platform || !username) {
        return res.status(400).json({ error: 'Platform and username are required' });
    }

    if (platform === 'roblox') {
        if (!ROBLOX_API_KEY || !ROBLOX_UNIVERSE_ID) {
            return res.status(500).json({ error: 'Roblox API key or Universe ID not configured' });
        }

        const userId = await getRobloxUserId(username);
        if (!userId) {
            return res.status(404).json({ error: 'Roblox user not found' });
        }

        try {
            // Get current banned list
            const getUrl = `https://apis.roblox.com/datastores/v1/universes/${ROBLOX_UNIVERSE_ID}/standard-datastores/datastore/entries/entry`;
            const getParams = {
                datastoreName: 'BannedUsers',
                entryKey: 'BannedList'
            };
            const headers = { 'x-api-key': ROBLOX_API_KEY };

            let bannedList = [];
            try {
                const getResponse = await axios.get(getUrl, { params: getParams, headers });
                bannedList = getResponse.data || [];
            } catch (getError) {
                if (getError.response && getError.response.status !== 404) {
                    throw getError;
                }
                // If 404, bannedList remains empty
            }

            // Add user if not already banned
            if (!bannedList.includes(userId)) {
                bannedList.push(userId);
            }

            // Update banned list
            const setParams = {
                datastoreName: 'BannedUsers',
                entryKey: 'BannedList'
            };
            await axios.post(getUrl, bannedList, { params: setParams, headers });

            console.log(`Banned Roblox user ${username} (ID: ${userId}) for reason: ${reason}`);
            res.json({ success: true, message: `Roblox user ${username} has been banned`, userId, reason });
        } catch (error) {
            console.error('Error banning Roblox user:', error.message);
            res.status(500).json({ error: 'Failed to ban Roblox user' });
        }
    } else {
        res.status(400).json({ error: 'Unsupported platform. Only "roblox" is supported for now.' });
    }
});

// GET endpoint for retrieving ban list
app.get('/banlist', async (req, res) => {
    const { platform } = req.query;

    if (!platform) {
        return res.status(400).json({ error: 'Platform is required' });
    }

    if (platform === 'roblox') {
        if (!ROBLOX_API_KEY || !ROBLOX_UNIVERSE_ID) {
            return res.status(500).json({ error: 'Roblox API key or Universe ID not configured' });
        }

        try {
            const getUrl = `https://apis.roblox.com/datastores/v1/universes/${ROBLOX_UNIVERSE_ID}/standard-datastores/datastore/entries/entry`;
            const params = {
                datastoreName: 'BannedUsers',
                entryKey: 'BannedList'
            };
            const headers = { 'x-api-key': ROBLOX_API_KEY };

            const response = await axios.get(getUrl, { params, headers });
            const bannedList = response.data || [];

            res.json({ success: true, bannedUsers: bannedList });
        } catch (error) {
            if (error.response && error.response.status === 404) {
                // No banned list exists yet
                res.json({ success: true, bannedUsers: [] });
            } else {
                console.error('Error retrieving ban list:', error.message);
                res.status(500).json({ error: 'Failed to retrieve ban list' });
            }
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
