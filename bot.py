import discord
from discord import app_commands
from discord.ext import commands
import gspread
import os
import requests
import json

# Load environment variables manually to handle multi-line JSON
def load_env_vars():
    env_vars = {}
    env_path = os.path.join(os.path.dirname(__file__), '.env')

    if os.path.exists(env_path):
        with open(env_path, 'r', encoding='utf-8') as f:
            content = f.read()

        lines = content.split('\n')
        current_key = None
        current_value = []

        for line in lines:
            line = line.strip()
            if not line or line.startswith('#'):
                continue

            if '=' in line and not current_key:
                # Start of a new variable
                key, value = line.split('=', 1)
                key = key.strip()
                value = value.strip()

                if key == 'GOOGLE_SHEETS_CREDENTIALS' and value.startswith('{'):
                    # Multi-line JSON detected
                    current_key = key
                    current_value = [value]
                else:
                    # Regular variable
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    env_vars[key] = value
            elif current_key == 'GOOGLE_SHEETS_CREDENTIALS':
                # Continue reading multi-line JSON
                current_value.append(line)
                if line.strip().endswith('}'):
                    # End of JSON
                    json_str = '\n'.join(current_value)
                    if json_str.startswith('"') and json_str.endswith('"'):
                        json_str = json_str[1:-1]
                    env_vars[current_key] = json_str
                    current_key = None
                    current_value = []

        # Set environment variables
        for key, value in env_vars.items():
            os.environ[key] = value

    return env_vars

env_vars = load_env_vars()

DISCORD_TOKEN = env_vars.get('DISCORD_TOKEN')
GOOGLE_CREDENTIALS = env_vars.get('GOOGLE_SHEETS_CREDENTIALS')
SPREADSHEET_ID = env_vars.get('SPREADSHEET_ID')
GUILD_ID = int(env_vars.get('GUILD_ID'))
GUILD = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# google Sheets setup
import json
from io import StringIO

def get_gspread_client():
    try:
        # Parse the JSON credentials
        creds_json = json.loads(GOOGLE_CREDENTIALS)
        client = gspread.service_account_from_dict(creds_json)
        print("Google Sheets integration initialized successfully")
        return client
    except Exception as e:
        print(f"Google Sheets setup failed: {e}")
        print("Bot will continue without Google Sheets integration")
        return None

gc = get_gspread_client()

sheet = None
try:
    if gc:
        sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
except Exception as e:
    print(f"Failed to open Google Sheet: {e}")
    sheet = None

# switch to commands.Bot for slash commands support
bot = commands.Bot(command_prefix="312.", intents=intents)

@bot.event
async def on_ready():
    print(f'readied: {bot.user}')
    try:
        synced = await bot.tree.sync(guild=GUILD)
        print(f'synced {len(synced)} commands to guild {GUILD.id}')
    except Exception as e:
        print(f'i fucking failed to sync these commands: {e}')

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    if str(message.channel.id) == "1417246932115390566" or str(message.channel.id) == "1417915609391300658":
        # save the message content to Sheets
        if sheet is not None:
            sheet.append_row([str(message.content)])
            print(f'saved message to Announcement Sheets: {message.content}')
        else:
            print(f'Google Sheets not available, skipping save for message: {message.content}')

# send DM and ban user
async def ban_discord_user(guild: discord.Guild, user: discord.Member, reason: str):
    try:
        dm_message = f"You have been banned from {guild.name}.\nReason: {reason}\nYou can appeal here: https://appealexample.com"
        await user.send(dm_message)
    except Exception as e:
        print(f"failed to DM {user}: {e}")
    await guild.ban(user, reason=reason)
    print(f"banned {user} for reason: {reason}")

# functions for roblox ban system

def roblox_ban_user(username: str, reason: str, duration: str = None):
    """
    Ban a user on Roblox using the local API server.
    """
    api_url = os.getenv('API_SERVER_URL', 'http://localhost:3000')

    try:
        payload = {
            "platform": "roblox",
            "username": username,
            "reason": reason
        }
        if duration:
            payload["duration"] = duration

        response = requests.post(f"{api_url}/ban", json=payload)

        if response.status_code == 200:
            data = response.json()
            duration_msg = f" for {duration}" if duration else ""
            print(f"Banned Roblox user {username} for reason: {reason}{duration_msg}")
            return True
        else:
            print(f"Failed to ban user: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error communicating with API server: {e}")
        return False

def roblox_unban_user(username: str):
    """
    Unban a user on Roblox using the local API server.
    """
    api_url = os.getenv('API_SERVER_URL', 'http://localhost:3000')

    try:
        response = requests.post(f"{api_url}/unban", json={
            "platform": "roblox",
            "username": username
        })

        if response.status_code == 200:
            data = response.json()
            print(f"Unbanned Roblox user {username}")
            return True
        else:
            print(f"Failed to unban user: {response.status_code} - {response.text}")
            return False
    except Exception as e:
        print(f"Error communicating with API server: {e}")
        return False

def get_roblox_ban_list():
    """
    Get the Roblox ban list from the local API server.
    """
    api_url = os.getenv('API_SERVER_URL', 'http://localhost:3000')

    try:
        response = requests.get(f"{api_url}/banlist", params={"platform": "roblox"})

        if response.status_code == 200:
            data = response.json()
            return data.get('bannedUsers', [])
        else:
            print(f"Failed to get ban list: {response.status_code} - {response.text}")
            return []
    except Exception as e:
        print(f"Error communicating with API server: {e}")
        return []

# chek if user has the right perms to ban
def has_ban_permission(interaction: discord.Interaction) -> bool:
    if interaction.user.guild_permissions.administrator:
        return True
    allowed_role_ids = [1417178366347448402, 1417178462216519831]
    user_roles = [role.id for role in interaction.user.roles]
    return any(role_id in allowed_role_ids for role_id in user_roles)

# command for banning users
@bot.tree.command(name="ban", description="Ban a user on Discord or Roblox")
@app_commands.guilds(GUILD)   # <-- make it server-scoped
@app_commands.describe(
    platform="the platform to ban user on (discord or roblox)",
    discord_user="discord user to ban (required if platform is discord)",
    roblox_username="roblox username to ban (required if platform is roblox)",
    reason="reason for the ban",
    duration="ban duration (e.g., 30s, 1m, 5h, 10d, 2y) - only for Roblox bans"
)
@app_commands.choices(platform=[
    app_commands.Choice(name="discord", value="discord"),
    app_commands.Choice(name="roblox", value="roblox")
])
async def ban(interaction: discord.Interaction, platform: app_commands.Choice[str], discord_user: discord.Member = None, roblox_username: str = None, reason: str = "No reason provided", duration: str = None):
    if not has_ban_permission(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return
    if platform.value == "discord":
        if discord_user is None:
            await interaction.response.send_message("You must specify a Discord user to ban.", ephemeral=True)
            return
        await interaction.response.defer()
        await ban_discord_user(interaction.guild, discord_user, reason)
        await interaction.followup.send(f"Discord user {discord_user} has been banned. Reason: {reason}")
    elif platform.value == "roblox":
        if roblox_username is None:
            await interaction.response.send_message("You must specify a Roblox username to ban.", ephemeral=True)
            return
        await interaction.response.defer()
        success = roblox_ban_user(roblox_username, reason, duration)
        if success:
            duration_msg = f" for {duration}" if duration else ""
            await interaction.followup.send(f"Roblox user {roblox_username} has been banned{duration_msg}. Reason: {reason}")
        else:
            await interaction.followup.send(f"Failed to ban Roblox user {roblox_username}.", ephemeral=True)

# command for unbanning users
@bot.tree.command(name="unban", description="Unban a user on Roblox")
@app_commands.guilds(GUILD)   # <-- make it server-scoped
@app_commands.describe(
    roblox_username="roblox username to unban"
)
async def unban(interaction: discord.Interaction, roblox_username: str):
    if not has_ban_permission(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer()
    success = roblox_unban_user(roblox_username)
    if success:
        await interaction.followup.send(f"Roblox user {roblox_username} has been unbanned.")
    else:
        await interaction.followup.send(f"Failed to unban Roblox user {roblox_username}.", ephemeral=True)

# command for getting ban list with pagination
@bot.tree.command(name="getbanlist", description="Get the list of banned Roblox users")
@app_commands.guilds(GUILD)   # <-- make it server-scoped
async def getbanlist(interaction: discord.Interaction):
    if not has_ban_permission(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer()

    banned_users = get_roblox_ban_list()
    if not banned_users:
        await interaction.followup.send("No banned users found.")
        return

    # Pagination setup
    items_per_page = 5
    total_pages = (len(banned_users) + items_per_page - 1) // items_per_page

    # Create embed for first page
    embed = discord.Embed(title="Banned Roblox Users", color=0xff0000)

    # Display current page (starting from 1)
    current_page = 1
    start_idx = (current_page - 1) * items_per_page
    end_idx = min(start_idx + items_per_page, len(banned_users))

    ban_list_text = ""
    for i in range(start_idx, end_idx):
        ban = banned_users[i]
        username = ban.get('username', f'User {ban["userId"]}')
        reason = ban.get('reason', 'No reason')
        duration = ban.get('duration', 'Permanent')
        expires_at = ban.get('expiresAt')

        if expires_at:
            expires_date = f"<t:{int(expires_at / 1000)}:R>"
        else:
            expires_date = "Never"

        ban_list_text += f"**{username}** (ID: {ban['userId']})\n"
        ban_list_text += f"Reason: {reason}\n"
        ban_list_text += f"Duration: {duration} | Expires: {expires_date}\n\n"

    embed.description = ban_list_text
    embed.set_footer(text=f"Page {current_page}/{total_pages}")

    # Add navigation buttons if more than one page
    if total_pages > 1:
        view = BanListView(banned_users, items_per_page, total_pages, current_page)
        await interaction.followup.send(embed=embed, view=view)
    else:
        await interaction.followup.send(embed=embed)

# View class for pagination buttons
class BanListView(discord.ui.View):
    def __init__(self, banned_users, items_per_page, total_pages, current_page):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.banned_users = banned_users
        self.items_per_page = items_per_page
        self.total_pages = total_pages
        self.current_page = current_page

    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages:
            self.current_page += 1
            await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Banned Roblox Users", color=0xff0000)

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.banned_users))

        ban_list_text = ""
        for i in range(start_idx, end_idx):
            ban = self.banned_users[i]
            username = ban.get('username', f'User {ban["userId"]}')
            reason = ban.get('reason', 'No reason')
            duration = ban.get('duration', 'Permanent')
            expires_at = ban.get('expiresAt')

            if expires_at:
                expires_date = f"<t:{int(expires_at / 1000)}:R>"
            else:
                expires_date = "Never"

            ban_list_text += f"**{username}** (ID: {ban['userId']})\n"
            ban_list_text += f"Reason: {reason}\n"
            ban_list_text += f"Duration: {duration} | Expires: {expires_date}\n\n"

        embed.description = ban_list_text
        embed.set_footer(text=f"Page {self.current_page}/{self.total_pages}")

        await interaction.response.edit_message(embed=embed, view=self)

# command for restoring items
@bot.tree.command(name="restore", description="Queue items for restoration when user returns to Roblox game")
@app_commands.guilds(GUILD)   # <-- make it server-scoped
@app_commands.describe(
    username="roblox username to restore items for",
    items="items to restore (comma-separated list)"
)
async def restore(interaction: discord.Interaction, username: str, items: str):
    if not has_ban_permission(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer()

    # requst
    api_url = os.getenv('API_SERVER_URL', 'http://localhost:3000')
    payload = {
        "username": username,
        "items": items
    }

    try:
        response = requests.post(f"{api_url}/restore", json=payload)

        if response.status_code == 200:
            data = response.json()
            await interaction.followup.send(f"✅ Items queued for restoration: **{username}**\nItems: {items}")
        else:
            error_data = response.json()
            await interaction.followup.send(f"❌ Failed to queue restoration: {error_data.get('error', 'Unknown error')}", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error communicating with API server: {str(e)}", ephemeral=True)

# command for getting restoration requests
@bot.tree.command(name="restorerequests", description="Get the list of pending restoration requests")
@app_commands.guilds(GUILD)   # <-- make it server-scoped
async def restorerequests(interaction: discord.Interaction):
    if not has_ban_permission(interaction):
        await interaction.response.send_message("You do not have permission to use this command.", ephemeral=True)
        return

    await interaction.response.defer()

    # Get restoration queue from API server
    api_url = os.getenv('API_SERVER_URL', 'http://localhost:3000')

    try:
        response = requests.get(f"{api_url}/restorationqueue")

        if response.status_code == 200:
            data = response.json()
            restoration_queue = data.get('queue', [])

            if not restoration_queue:
                await interaction.followup.send("No pending restoration requests found.")
                return

            # Pagination setup
            items_per_page = 5
            total_pages = (len(restoration_queue) + items_per_page - 1) // items_per_page

            # Create embed for first page
            embed = discord.Embed(title="Pending Restoration Requests", color=0x00ff00)

            # Display current page (starting from 1)
            current_page = 1
            start_idx = (current_page - 1) * items_per_page
            end_idx = min(start_idx + items_per_page, len(restoration_queue))

            restoration_text = ""
            for i in range(start_idx, end_idx):
                entry = restoration_queue[i]
                username = entry.get('username', 'Unknown')
                items = entry.get('items', [])
                queued_at = entry.get('queuedAt')

                if queued_at:
                    queued_date = f"<t:{int(queued_at / 1000)}:R>"
                else:
                    queued_date = "Unknown"

                restoration_text += f"**{username}**\n"
                restoration_text += f"Items: {', '.join(items)}\n"
                restoration_text += f"Queued: {queued_date}\n\n"

            embed.description = restoration_text
            embed.set_footer(text=f"Page {current_page}/{total_pages}")

            # Add navigation buttons if more than one page
            if total_pages > 1:
                view = RestorationRequestsView(restoration_queue, items_per_page, total_pages, current_page)
                await interaction.followup.send(embed=embed, view=view)
            else:
                await interaction.followup.send(embed=embed)
        else:
            await interaction.followup.send("❌ Failed to fetch restoration requests.", ephemeral=True)
    except Exception as e:
        await interaction.followup.send(f"❌ Error communicating with API server: {str(e)}", ephemeral=True)

# View class for restoration requests pagination buttons
class RestorationRequestsView(discord.ui.View):
    def __init__(self, restoration_queue, items_per_page, total_pages, current_page):
        super().__init__(timeout=300)  # 5 minutes timeout
        self.restoration_queue = restoration_queue
        self.items_per_page = items_per_page
        self.total_pages = total_pages
        self.current_page = current_page

    @discord.ui.button(label="⬅️ Previous", style=discord.ButtonStyle.primary)
    async def previous_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page > 1:
            self.current_page -= 1
            await self.update_embed(interaction)

    @discord.ui.button(label="➡️ Next", style=discord.ButtonStyle.primary)
    async def next_page(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.current_page < self.total_pages:
            self.current_page += 1
            await self.update_embed(interaction)

    async def update_embed(self, interaction: discord.Interaction):
        embed = discord.Embed(title="Pending Restoration Requests", color=0x00ff00)

        start_idx = (self.current_page - 1) * self.items_per_page
        end_idx = min(start_idx + self.items_per_page, len(self.restoration_queue))

        restoration_text = ""
        for i in range(start_idx, end_idx):
            entry = self.restoration_queue[i]
            username = entry.get('username', 'Unknown')
            items = entry.get('items', [])
            queued_at = entry.get('queuedAt')

            if queued_at:
                queued_date = f"<t:{int(queued_at / 1000)}:R>"
            else:
                queued_date = "Unknown"

            restoration_text += f"**{username}**\n"
            restoration_text += f"Items: {', '.join(items)}\n"
            restoration_text += f"Queued: {queued_date}\n\n"

        embed.description = restoration_text
        embed.set_footer(text=f"Page {self.current_page}/{self.total_pages}")

        await interaction.response.edit_message(embed=embed, view=self)

bot.run(DISCORD_TOKEN)
