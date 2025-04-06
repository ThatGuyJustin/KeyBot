# Keys Giveaway Bot
## My friend needed a system to give away a bunch of game codes. This was the result.
### You're welcome solace.

# Setup
## Docker Compose
Honestly, I recommend just using the compose.yaml file to pull the pre-built image from the github container registry, or use the dev.yaml if you plan to add/change things with the image.

## For those who hate Docker.
> Python 3.12 & Poetry are used. 
1. git clone https://github.com/ThatGuyJustin/KeyBot.git
2. `poetry install`
3. Add `FREE_KEYS_CHANNEL` to a `.env` file in the root project directory
4. poetry run python -m disco.cli --token DISCORD_TOKEN

## Environment Variables
`DISCORD_TOKEN`: Bot token from [Discord's Developer Dashboard](https://discord.com/developers/applications)

`FREE_KEYS_CHANNEL`: Channel where you intend the bot to post keys in.

# Usage

## Commands
> Note: Commands are all registered on startup when the bot connects to the gateway.

### Slash Commands
`/add-key` - Lets you add a key. (***By default it requires Manage Server permissions.***)

### Message Commands (When a message is right-clicked.)
`Get Key Info` - When used on a key message, it will give you all the information about it. (***By default it requires Manage Server permissions.***)

* General information about the key (*Title, platform*)
* When it was submitted
* Who submitted it
* The key (*Spoiler Tagged*)
* Claim information (*User, and timestamp*)

## How it works
When a key is posted by the bot, there is a claim button attached. 

When the button is pressed, it will edit the message to disable the button and DM the person who clicked it the key for the product they've claimed.

The bot will save the information about the claim to the database for lookup later.