import discord
from discord import app_commands
from discord.ext import commands
import gspread
import os
import requests
from dotenv import load_dotenv

load_dotenv()

DISCORD_TOKEN = os.getenv('DISCORD_TOKEN')
GOOGLE_CREDENTIALS = os.getenv('GOOGLE_SHEETS_CREDENTIALS')
SPREADSHEET_ID = os.getenv('SPREADSHEET_ID')
GUILD_ID = int(os.getenv('GUILD_ID'))
GUILD = discord.Object(id=GUILD_ID)

intents = discord.Intents.default()
intents.messages = True
intents.message_content = True

# google Sheets setup
gc = gspread.service_account(filename=GOOGLE_CREDENTIALS)

try:
    sheet = gc.open_by_key(SPREADSHEET_ID).sheet1
except gspread.exceptions.APIError as e:
    print(f"GSA error: {e}")
    raise

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

    if str(message.channel.id) == "1417246932115390566":
        # save the message content to Sheets
        sheet.append_row([str(message.content)])
        print(f'saved message to Announcement Sheets: {message.content}')

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

def roblox_ban_user(username: str, reason: str):
    """
    Ban a user on Roblox using the local API server.
    """
    api_url = os.getenv('API_SERVER_URL', 'http://localhost:3000')

    try:
        response = requests.post(f"{api_url}/ban", json={
            "platform": "roblox",
            "username": username,
            "reason": reason
        })

        if response.status_code == 200:
            data = response.json()
            print(f"Banned Roblox user {username} for reason: {reason}")
            return True
        else:
            print(f"Failed to ban user: {response.status_code} - {response.text}")
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
    reason="reason for the ban"
)
@app_commands.choices(platform=[
    app_commands.Choice(name="discord", value="discord"),
    app_commands.Choice(name="roblox", value="roblox")
])
async def ban(interaction: discord.Interaction, platform: app_commands.Choice[str], discord_user: discord.Member = None, roblox_username: str = None, reason: str = "No reason provided"):
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
        success = roblox_ban_user(roblox_username, reason)
        if success:
            await interaction.followup.send(f"Roblox user {roblox_username} has been banned. Reason: {reason}")
        else:
            await interaction.followup.send(f"Failed to ban Roblox user {roblox_username}.", ephemeral=True)

bot.run(DISCORD_TOKEN)
