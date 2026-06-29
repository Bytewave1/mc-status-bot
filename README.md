# MC Status Bot

A Discord bot that displays the live status of a Minecraft Java server.

## Features

- Live server status with auto-updating embed
- Player count, version, latency and MOTD display
- Bot presence shows current player count
- Configurable server IP, port and update interval
- Admin commands to change server and status channel on the fly

## Setup

1. Clone the repo
```bash
git clone https://github.com/yourusername/mc-status-bot.git
cd mc-status-bot
```

2. Install dependencies
```bash
pip install -r requirements.txt
```

3. Copy `config.example.json` to `config.json` and fill in your values
```bash
cp config.example.json config.json
```

| Field | Description |
|-------|-------------|
| `token` | Your Discord bot token |
| `server_ip` | Minecraft server IP |
| `server_port` | Minecraft server port (default 25565) |
| `update_interval` | Status update interval in seconds |
| `embed_color` | Hex color for the embed |
| `status_channel_id` | Channel ID for auto-updating status (or set via command) |

4. Run the bot
```bash
python main.py
```

## Commands

| Command | Permission | Description |
|---------|-----------|-------------|
| `!status` | Everyone | Shows the current server status |
| `!setserver <ip> [port]` | Admin | Changes the monitored server |
| `!setchannel` | Admin | Sets the current channel as the status channel |

## Requirements

- Python 3.9+
- discord.py 2.3+
- mcstatus 11.0+
