import os
import sys
import hashlib
from typing import Dict
from twitchio.ext import commands
from twitchio.dataclasses import User
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
	initial_channels=["#" + os.environ['CHANNEL']]
)

channel = None

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
	global bot, channel
	channel = bot.get_channel(os.environ['CHANNEL'])
	if channel:
		await channel.send("Connected to chat.")
	else:
		print("Not connected to expected channel: " + os.environ['CHANNEL'])


def write_command(command_name: str, params: Dict[str, str] = {}):
	command = command_name
	for param_name in params:
		command += "|"
		command += f"{param_name}^{params[param_name]}"
	print(f"Writing command to file: {command}")
	file = open(command_file, "a")
	file.writelines(command + os.linesep)
	file.close()


def get_name_colour(author: User) -> str:
	global name_colour_list, name_colour_dictionary
	colour = name_colour_dictionary.get(author.colour)
	if not colour:
		name_hash = int(hashlib.md5(author.name.encode('utf-8')).hexdigest(), 16)
		colour = name_colour_list[name_hash % len(name_colour_list)]
	return colour


@bot.command(name='char', aliases=['character'])
async def change_character(ctx):
	print(f"received command {ctx.content}")
	words = ctx.content.split(' ')
	params = {}
	if len(words) > 1:
		if words[1].lower() == 'random':
			params['colour'] = 'random'
		else:
			params['character'] = words[1].lower()
	write_command("CHARACTER", params)


@bot.event
async def event_message(ctx):
	await bot.handle_commands(ctx)
	colour = get_name_colour(ctx.author)
	write_command("CHAT", {"username": ctx.author.name, "message": ctx.content, "namecolour": colour})


if __name__ == "__main__":
	bot.run()
