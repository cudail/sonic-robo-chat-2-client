import math
import os
import sys
import hashlib
import random
import yaml
from typing import Dict, Optional
from twitchio.ext import commands
from twitchio.dataclasses import User, Context, Message

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

oauth_token = config['oauth_token']
if not oauth_token.startswith("oauth:"):
	oauth_token = "oauth:" + oauth_token

command_prefix = config.get('command_prefix', "!")

# Initialise bot
bot = commands.Bot(
	irc_token=oauth_token,
	nick=config['bot_nick'],
	prefix=command_prefix,
	initial_channels=["#" + config['channel']]
)


subscriber_only = config.get('subscriber_only', [])
mod_only = config.get('mod_only', [])
disabled = config.get('disabled', [])
min_bits = config.get('min_bits', {})


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

queue = []


@bot.event
async def event_ready():
	print("Bot started.")
	global bot, channel
	channel = bot.get_channel(config['channel'])
	if not channel:
		print("Not connected to expected channel: " + config['channel'])
	elif config.get('join_message'):
		await channel.send(config['join_message'])


def write_command(command_name: str, params: Dict[str, str] = None):
	if params is None:
		params = {}
	command = command_name
	for param_name in params:
		command += "|"
		command += f"{param_name}^{params[param_name]}"
	if config.get('write_immediately'):
		print(f"Writing command to file: {command}")
		file = open(command_file, "a")
		file.writelines(command + os.linesep)
		file.close()
	else:
		# add commands queue and wait until the mod as cleared the existing file
		# before writing to it
		print(f"Adding command to queue: {command}")
		global queue
		queue.append(command)
		if not os.path.exists(command_file) or os.stat(command_file).st_size == 0:
			print("Writing commands to file.")
			file = open(command_file, "a")
			file.writelines(os.linesep.join(queue))
			file.close()
			queue = []


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


def bits_used(message: Message) -> int:
	if message.tags and 'bits' in message.tags:
		bits = parse_int(message.tags['bits'])
		if bits:
			return bits
	return 0


def handle_command(name: str, context: Context) -> str:
	print(f"received command {context.content}")
	global disabled, subscriber_only, mod_only, min_bits
	if not context.author.is_mod:
		if name in disabled:
			return f"Command {name} is disabled, ignoring."
		if name in mod_only:
			return f"Command {name} is mod only, ignoring."
		if name in subscriber_only and not context.author.is_subscriber:
			return f"Command {name} is subscriber only, ignoring"
		if name in min_bits:
			bits_needed = parse_int(min_bits[name])
			bits_received = bits_used(context.message)
			if bits_needed > bits_received:
				return f"Command {name} needs {bits_needed} but {bits_received} were received."


# Character commands
@bot.command()
async def char(ctx: Context):
	error = handle_command('char', ctx)
	if error is not None:
		print(error)
		return
	words = ctx.content.split(' ')
	params = {}
	if len(words) > 1:
		if words[1].lower() == 'rcolour':
			params['colour'] = 'random'
		else:
			params['character'] = words[1].lower()
			if len(words) > 2 and words[2].lower() == 'rcolour':
				params['colour'] = 'random'
	write_command("CHARACTER", params)


@bot.command()
async def ring(ctx: Context):
	error = handle_command('ring', ctx)
	if error is not None:
		print(error)
		return
	bpr = parse_int(config.get('bits_per_ring', 0))
	if bpr and bpr > 0:
		bits_received = bits_used(ctx.message)
		if bits_received > 0:
			m = math.floor(bits_received / bpr)
			for i in range(0, m):
				write_command("RING")
			return
	write_command("RING")


@bot.command()
async def unring(ctx: Context):
	error = handle_command('unring', ctx)
	if error is not None:
		print(error)
		return
	bpu = parse_int(config.get('bits_per_unring', 0))
	if bpu and bpu > 0:
		bits_received = bits_used(ctx.message)
		if bits_received > 0:
			m = math.floor(bits_received / bpu)
			for i in range(0, m):
				write_command("UNRING")
			return
	write_command("UNRING")


@bot.command(name='1up')
async def oneup(ctx: Context):
	error = handle_command('1up', ctx)
	if error is not None:
		print(error)
		return
	write_command("1UP")


@bot.command()
async def air(ctx: Context):
	error = handle_command('air', ctx)
	if error is not None:
		print(error)
		return
	write_command("AIR")


@bot.command()
async def scale(ctx: Context):
	error = handle_command('scale', ctx)
	if error is not None:
		print(error)
		return
	words = ctx.content.split(' ')
	if len(words) < 2:
		print("scale command did not have an argument, ignoring")
		return
	char_scale = parse_float(words[1])
	if char_scale is None:
		print("scale was not a valid number, ignoring")
		return
	if char_scale < 0.1:
		char_scale = 0.1
	if char_scale > 10:
		char_scale = 10
	write_command("SCALE", {"scale": str(char_scale), "duration": 35 * 30})


# Follower commands
@bot.command()
async def swap(ctx: Context):
	error = handle_command('swap', ctx)
	if error is not None:
		print(error)
		return
	write_command("SWAP")


@bot.command()
async def foll(ctx: Context):
	error = handle_command('foll', ctx)
	if error is not None:
		print(error)
		return
	words = ctx.content.split(' ')
	params = {}
	if len(words) > 1:
		if words[1].lower() == 'rcolour':
			params['colour'] = 'random'
		else:
			params['character'] = words[1].lower()
			if len(words) > 2 and words[2].lower() == 'rcolour':
				params['colour'] = 'random'
	write_command("FOLLOWER", params)


# Spawning object commands
@bot.command()
async def obj(ctx: Context):
	error = handle_command('obj', ctx)
	if error is not None:
		print(error)
		return
	words = ctx.content.split(' ')
	if len(words) < 2:
		print("Object command did not include an ID, ignoring")
		return
	object_id = words[1]
	message = " ".join(words[2:])
	colour = get_name_colour(ctx.author)
	params = {"username": ctx.author.name, "namecolour": colour,
		"message": message, "objectid": object_id}
	write_command("OBJECT", params)


@bot.command()
async def badnik(ctx: Context):
	error = handle_command('badnik', ctx)
	if error is not None:
		print(error)
		return
	message = " ".join(ctx.content.split(' ')[1:])
	params = {"username": ctx.author.name,
		"namecolour": get_name_colour(ctx.author), "message": message}
	write_command("BADNIK", params)


@bot.command()
async def monitor(ctx: Context):
	error = handle_command('monitor', ctx)
	if error is not None:
		print(error)
		return
	message = " ".join(ctx.content.split(' ')[1:])
	params = {"username": ctx.author.name,
		"namecolour": get_name_colour(ctx.author), "message": message}
	write_command("MONITOR", params)


@bot.command()
async def spring(ctx: Context):
	error = handle_command('spring', ctx)
	if error is not None:
		print(error)
		return
	colours = ['blue', 'yellow', 'red']
	orientation = ['horizontal', 'vertical', 'diagonal']
	direction = ['forward', 'back', 'left', 'right']
	write_command("SPRING", {"colour": random.choice(colours),
		"orientation": random.choice(orientation),
		"direction": random.choice(direction)})


# Sound commands
@bot.command()
async def sfx(ctx: Context):
	error = handle_command('sfx', ctx)
	if error is not None:
		print(error)
		return
	words = ctx.content.split(' ')
	if len(words) < 2:
		print("sfx command did not have an argument, ignoring")
		return
	write_command("SOUND", {"sound": words[1]})


@bot.command()
async def bgm(ctx: Context):
	error = handle_command('bgm', ctx)
	if error is not None:
		print(error)
		return
	words = ctx.content.split(' ')
	if len(words) < 2:
		print("music command did not have an argument, ignoring")
		return
	write_command("MUSIC", {"track": words[1].upper()})


# Config commands
@bot.command(name='config')
async def config_command(ctx: Context):
	error = handle_command('config', ctx)
	if error is not None:
		print(error)
		return
	words = ctx.content.split(' ')
	if len(words) < 3:
		print("config command did not have enough arguments, ignoring.")
		return
	write_command("CONFIG", {"setting": words[1], "value": words[2]})


@bot.command()
async def killall(ctx: Context):
	error = handle_command('killall', ctx)
	if error is not None:
		print(error)
		return
	write_command("KILLALL")


@bot.command()
async def despawn(ctx: Context):
	error = handle_command('despawn', ctx)
	if error is not None:
		print(error)
		return
	write_command("DESPAWN")


# Message handing
@bot.event
async def event_message(ctx: Context):
	for character in "|^\r\n":  # Strip dangerous characters
		ctx.content = ctx.content.replace(character, ' ')
	await bot.handle_commands(ctx)
	colour = get_name_colour(ctx.author)
	if not config.get('display_chat_messages'):
		return
	global command_prefix
	if ctx.content.startswith(command_prefix) and not config.get('display_chat_commands'):
		return
	if ctx.author.name == bot.nick and not config.get('display_bot_messages'):
		return
	write_command("CHAT", {"username": ctx.author.name, "message": ctx.content,
		"namecolour": colour})


if __name__ == "__main__":
	bot.run()
