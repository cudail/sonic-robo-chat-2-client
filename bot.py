import os
import sys
from typing import Dict
from twitchio.ext import commands
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


# Check for chat command file
luafiles_dir = os.environ['SRB2_LUAF_DIR']
if os.path.isdir(luafiles_dir):
    print(f"Found luafiles directory at {luafiles_dir}")
else:
    print(f"Could not find luafiles directory at {luafiles_dir}")
    sys.exit(1)
command_file = os.path.join(luafiles_dir, "chat_commands.txt")
print(f"Using command file {command_file}")


# Initialise bot
bot = commands.Bot(
    irc_token=os.environ['TMI_TOKEN'],
    client_id=os.environ['CLIENT_ID'],
    nick=os.environ['BOT_NICK'],
    prefix=os.environ['BOT_PREFIX'],
    initial_channels=[os.environ['CHANNEL']]
)


@bot.event
async def event_ready():
    """Called once when the bot goes online."""
    print("Bot started.")
    await bot._ws.send_privmsg(os.environ['CHANNEL'], "Connected to chat.")


def write_command(command_name: str, params: Dict[str, str] = {}):
    command = command_name
    for param_name in params:
        command += "|"
        command += f"{param_name}^{params[param_name]}"
    file = open(command_file, "a")
    file.writelines(command + os.linesep)
    file.close()


@bot.command(name='char')
async def change_character(ctx):
    print(f"received command {ctx.content}")
    write_command("CHARACTER")


if __name__ == "__main__":
    bot.run()
