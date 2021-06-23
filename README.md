# Sonic Robo Chat 2 Client

This is a Twitch bot to go with the [Sonic Robo Chat 2] mod to allow you to
stream Sonic Robo Blast 2 with chat participation features. This is a command
line only script and does not come with any kind of graphical interface.


## Setup

First download and setup [Sonic Robo Chat 2] itself.

Then download the contents of this repository. It does not matter where on your
computer you save it.


### Twitch API

For the bot to function it will need to be able to log into a Twitch account.
This can be the same account you will be streaming from or one made just for the
bot. In either case you will need to generate an OAuth token and a client ID for
the account. On the [OAuth token page] you just need to authorise your account
and it will give you the token, which is just a string of letters and numbers.

To get a client ID you need to register the bot as an application with Twitch
on the [application registration page]. The name can be anything you like, the
OAuth Redirect URL should be set to "localhost" as you will be running it
locally, and set the Category to "Chat Bot".

[OAuth token page]: https://twitchapps.com/tmi/
[application registration page]: https://dev.twitch.tv/console/apps/create

### Configuration

Fill in the Twitch account details in `config.yaml`. The configuration file uses
the YAML format. Fill in the OAuth token and client ID in the first two lines.
Then enter the name of the account you're using for the bot for the `bot_nick`
and the channel you will be streaming from for `channel`. These can be the same
account. Finally set the `srb2_dir` to where ever Sonic Robo Blast 2 is
installed on your computer.

The other options in the configuration file are detailed in below in the section
**Chat Configuration**.


### Python

This bot requires Python 3 to run. Download the latest version of Python 3 from
the [official Python website]. Once you have Python 3 installed open the folder
you saved the files from this repository in in your preferred terminal or
command prompt.

You will need to install all of the requirements for the bot with Pip, Python's
package manager. To do this simply run

`pip3 install -r requirements.txt`

in the directory with the requirements.txt file.


[official Python website]: https://python.org

### Running

To run the client open the folder you saved this repository to and run:

`python3 sonic-robo-chat.py`

If you want to rename the configuration file, use a configuration in a different
directory or have different sets of configurations for different streams you can
also specify the name of the configuration file to use as an argument instead of
the default config.yaml file.

`python3 sonic-robo-chat.py path/to/other-config.yaml`


## Chat Configuration

The configuration file specifies the following options using YAML:

* `oauth_token`: Your bot's Twitch account OAuth token.
* `client_id`: A Twitch application client ID.
* `bot_nick`: The name of the account of your bot (all lowercase).
* `command_prefix`: The prefix for messages that indicates a command. E.g. if
  set to "#" the command to change character will be "#char". If it's "!" it
  will be "!char".
* `channel`: The name of the channel you will be streaming from.
* `srb2_dir`: The directory Sonic Robo Blast 2 is installed in.
* `join_message`: A message to display in chat when the bot starts.
* `display_chat_messages`: If set to `yes` then normal chat messages will be
  shown in-game
* `display_chat_commands`: If set to `yes` then chat commands will be shown
  in-game
* `display_bot_messages`: If set to `yes` then messages from the bot itself will
  be displayed in-game.
* `subscriber_only`: A list of commands that can only be used by subscribers.
* `mod_only`: A list of commands that can only be used by mods. Commands like
  `config`, `despawnall` and `killall` should probably be set here.
* `disabled`: A list of commands that are disabled entirely.
* `min_bits`: A dictionary specifying the amount of bits that each command should
  cost to use. E.g. if `char: 50` is set here then a message must have a cheer
  of at least 50 bits for the this command to work.
* `bits_per_ring`: Allows the `ring` command to be used with a cheer to give 
  more rings at once. E.g. if it's set to 2 and a user cheers with 100 bits then
  50 `ring` commands will be sent to the game. Users can still send ring command
  without a cheer to give one ring unless the `ring` command in also specified
  in the `min_bits` dictionary.
* `bits_per_unring`: The same as the above, but for the `unring` command.
