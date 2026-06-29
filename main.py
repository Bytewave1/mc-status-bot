import discord
from discord.ext import commands, tasks
from mcstatus import JavaServer
import json
import os

with open("config.json", "r") as f:
    config = json.load(f)

TOKEN = config["token"]
SERVER_IP = config["server_ip"]
SERVER_PORT = config["server_port"]
UPDATE_INTERVAL = config["update_interval"]
EMBED_COLOR = int(config["embed_color"], 16)
STATUS_CHANNEL_ID = config.get("status_channel_id")

bot = commands.Bot(command_prefix="!", intents=discord.Intents.default())
status_message = None


def query_server():
    try:
        server = JavaServer.lookup(f"{SERVER_IP}:{SERVER_PORT}")
        status = server.status()
        return {
            "online": True,
            "players": status.players.online,
            "max_players": status.players.max,
            "motd": status.description,
            "version": status.version.name,
            "latency": round(status.latency, 1)
        }
    except Exception:
        return {"online": False}


def build_embed(data):
    if data["online"]:
        embed = discord.Embed(
            title=f"{SERVER_IP}",
            color=discord.Color(EMBED_COLOR)
        )
        embed.add_field(name="Status", value="Online", inline=True)
        embed.add_field(name="Players", value=f"{data['players']}/{data['max_players']}", inline=True)
        embed.add_field(name="Version", value=data["version"], inline=True)
        embed.add_field(name="Latency", value=f"{data['latency']}ms", inline=True)
        embed.add_field(name="MOTD", value=str(data["motd"]), inline=False)
    else:
        embed = discord.Embed(
            title=f"{SERVER_IP}",
            color=discord.Color.red()
        )
        embed.add_field(name="Status", value="Offline", inline=True)

    embed.set_footer(text="MC Status Bot")
    return embed


@tasks.loop(seconds=UPDATE_INTERVAL)
async def update_status():
    global status_message

    if not STATUS_CHANNEL_ID:
        return

    channel = bot.get_channel(STATUS_CHANNEL_ID)
    if not channel:
        return

    data = query_server()
    embed = build_embed(data)

    if data["online"]:
        await bot.change_presence(
            activity=discord.Game(name=f"{data['players']}/{data['max_players']} online")
        )
    else:
        await bot.change_presence(
            activity=discord.Game(name="Server Offline"),
            status=discord.Status.dnd
        )

    if status_message:
        try:
            await status_message.edit(embed=embed)
            return
        except discord.NotFound:
            status_message = None

    status_message = await channel.send(embed=embed)


@bot.event
async def on_ready():
    print(f"Logged in as {bot.user}")
    if STATUS_CHANNEL_ID:
        update_status.start()


@bot.command(name="status")
async def cmd_status(ctx):
    data = query_server()
    embed = build_embed(data)
    await ctx.send(embed=embed)


@bot.command(name="setserver")
@commands.has_permissions(administrator=True)
async def cmd_setserver(ctx, ip: str, port: int = 25565):
    global SERVER_IP, SERVER_PORT

    SERVER_IP = ip
    SERVER_PORT = port

    config["server_ip"] = ip
    config["server_port"] = port
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    await ctx.send(f"Server updated to `{ip}:{port}`")


@bot.command(name="setchannel")
@commands.has_permissions(administrator=True)
async def cmd_setchannel(ctx):
    global STATUS_CHANNEL_ID, status_message

    STATUS_CHANNEL_ID = ctx.channel.id
    config["status_channel_id"] = ctx.channel.id
    with open("config.json", "w") as f:
        json.dump(config, f, indent=4)

    status_message = None

    if not update_status.is_running():
        update_status.start()

    await ctx.send(f"Status channel set to {ctx.channel.mention}")


bot.run(TOKEN)
