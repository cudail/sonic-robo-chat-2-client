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

name_colour_list = ["pink", "yellow", "green", "blue", "red", "grey",
										"orange", "sky", "purple", "aqua", "peridot", "azure", "brown", "rosy"]

name_colour_dictionary = {
	"#FF0000": "red",
	"#0000FF": "blue",
	"#008000": "aqua",
	"#B22222": "rosy",
	"#FF7F50": "brown",
	"#9ACD32": "peridot",
	"#FF4500": "orange",
	"#2E8B57": "aqua",
	"#DAA520": "yellow",
	"#D2691E": "brown",
	"#5F9EA0": "azure",
	"#1E90FF": "sky",
	"#FF69B4": "pink",
	"#8A2BE2": "purple",
	"#00FF7F": "green"
}


@bot.event
async def event_ready():
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


@bot.event
async def event_message(ctx):
	await bot.handle_commands(ctx)
	global name_colour_list, name_colour_dictionary
	colour = name_colour_dictionary[ctx.author.colour]
	if not colour:
		colour = hash(ctx.author.name) % len(name_colour_list)
	write_command("CHAT", {"username": ctx.author.name, "message": ctx.content, "namecolour": colour})


if __name__ == "__main__":
	bot.run()
