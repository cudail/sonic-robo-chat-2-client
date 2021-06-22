import os
import sys
import hashlib
import random
import yaml
from typing import Dict, Optional
from twitchio.ext import commands
from twitchio.dataclasses import User, Context

# Load config
if len(sys.argv) > 1:
	if os.path.exists(sys.argv[1]):
		config_file_name = sys.argv[1]
	else:
		print(f"cannot find specified config file {sys.argv[1]}")
		sys.exit(2)
else:
	if os.path.exists('config.yaml'):
		config_file_name = 'config.yaml'
	else:
		print("No config file specified and the default config file 'config.yaml' was not found")
		sys.exit(3)

with open(config_file_name) as config_file:
	config = yaml.load(config_file, Loader=yaml.FullLoader)

# Check for chat command file
luafiles_dir = os.path.join(config['srb2_dir'], 'luafiles')
if os.path.isdir(luafiles_dir):
	print(f"Found luafiles directory at {luafiles_dir}")
else:
	print(f"Could not find luafiles directory at {luafiles_dir}")
	sys.exit(1)
command_file = os.path.join(luafiles_dir, "chat_commands.txt")
print(f"Using command file {command_file}")

# Initialise bot
bot = commands.Bot(
	irc_token=config['oauth_token'],
	client_id=config['client_id'],
	nick=config['bot_nick'],
	prefix=config['command_prefix'],
	initial_channels=["#" + config['channel']]
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
	channel = bot.get_channel(config['channel'])
	if channel:
		await channel.send("Connected to chat.")
	else:
		print("Not connected to expected channel: " + config['channel'])


def write_command(command_name: str, params: Dict[str, str] = None):
	if params is None:
		params = {}
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


def parse_int(string: str) -> Optional[int]:
	try:
		i = int(string)
		return i
	except ValueError:
		return None


def parse_float(string: str) -> Optional[float]:
	try:
		f = float(string)
		return f
	except ValueError:
		return None


def handle_command(name: str, context: Context) -> str:
	print(f"received command {context.content}")
	if name in config['command_rules']['disabled']:
		return f"Command {name} is disabled, ignoring."
	if name in config['command_rules']['subscriber_only'] and not context.author.is_subscriber:
		return f"Command {name} is subscriber only, ignoring"
	if name in config['command_rules']['mod_only'] and not context.author.is_mod:
		return f"Command {name} is mod only, ignoring."
	if name in config['command_rules']['bits']:
		bits_needed = parse_int(config['command_rules']['bits'][name])
		if bits_needed is not None and bits_needed > 0:
			if not context.message.tags or not 'bits_used' in context.message.tags:
				return f"Command {name} needs {bits_needed} bits but message had none."
			bits_received = parse_int(context.message.tags['bits_used'])
			if bits_received is None:
				return f"Command {name} needs {bits_needed} bits but message had none."
			if bits_received < bits_needed:
				return f"Command {name} needs {bits_needed} but only {bits_received} were received."


# Character commands
@bot.command(name='char')
async def change_character(ctx):
	error = handle_command('char', ctx)
	if error is not None:
		print(error)
		return
	words = ctx.content.split(' ')
	params = {}
	if len(words) > 1:
		if words[1].lower() == 'random':
			params['colour'] = 'random'
		else:
			params['character'] = words[1].lower()
	write_command("CHARACTER", params)


@bot.command(name='ring')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	write_command("RING")


@bot.command(name='unring')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	write_command("UNRING")


@bot.command(name='1up')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	write_command("1UP")


@bot.command(name='air')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	write_command("AIR")


@bot.command(name='scale')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	words = ctx.content.split(' ')
	if len(words) < 2:
		print("scale command did not have an argument, ignoring")
		return
	scale = parse_float(words[1])
	if scale is None:
		print("scale was not a valid number, ignoring")
		return
	if scale < 0.1:
		scale = 0.1
	if scale > 10:
		scale = 10
	write_command("SCALE", {"scale": str(scale), "duration": 35*30})


# Follower commands
@bot.command(name='swap')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	write_command("SWAP")


@bot.command(name='foll')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	words = ctx.content.split(' ')
	params = {}
	if len(words) > 1:
		if words[1].lower() == 'random':
			params['colour'] = 'random'
		else:
			params['character'] = words[1].lower()
	write_command("FOLLOWER", params)


# Spawning object commands
@bot.command(name='obj')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	words = ctx.content.split(' ')
	if len(words) < 2:
		print("Object command did not include an ID, ignoring")
		return
	object_id = parse_int(words[1])
	if not object_id or object_id < 1:
		print("Object command did not contain a valid ID, ignoring")
		return
	message = " ".join(words[2:])
	colour = get_name_colour(ctx.author)
	params = {"username": ctx.author.name, "namecolour": colour, "message": message, "objectid": object_id}
	write_command("OBJECT", params)


@bot.command(name='badnik')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	message = " ".join(ctx.content.split(' ')[1:])
	params = {"username": ctx.author.name, "namecolour": get_name_colour(ctx.author), "message": message}
	write_command("BADNIK", params)


@bot.command(name='monitor')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	message = " ".join(ctx.content.split(' ')[1:])
	params = {"username": ctx.author.name, "namecolour": get_name_colour(ctx.author), "message": message}
	write_command("MONITOR", params)


@bot.command(name='spring')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	colours = ['blue', 'yellow', 'red']
	orientation = ['horizontal', 'vertical', 'diagonal']
	direction = ['forward', 'back', 'left', 'right']
	write_command("SPRING", {"colour": random.choice(colours), "orientation": random.choice(orientation),
		"direction": random.choice(direction)})


# Sound commands
@bot.command(name='sfx')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	words = ctx.content.split(' ')
	if len(words) < 2:
		print("sfx command did not have an argument, ignoring")
		return
	sfx_id = parse_int(words[1])
	if not sfx_id or sfx_id < 1:
		print("sfx command did not contain a sfx ID, ignoring")
		return
	write_command("SOUND", {"sound": str(sfx_id)})


@bot.command(name='bgm')
async def change_character(ctx):
	print(f"received command {ctx.content}")
	words = ctx.content.split(' ')
	if len(words) < 2:
		print("music command did not have an argument, ignoring")
		return
	write_command("MUSIC", {"track": words[1].upper()})


# Message handing
@bot.event
async def event_message(ctx):
	await bot.handle_commands(ctx)
	colour = get_name_colour(ctx.author)
	write_command("CHAT", {"username": ctx.author.name, "message": ctx.content, "namecolour": colour})


if __name__ == "__main__":
	bot.run()
