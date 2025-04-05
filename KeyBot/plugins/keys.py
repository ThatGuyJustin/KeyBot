import os
from datetime import datetime, UTC as UTC_TIMEZONE

import yaml
from disco.bot import Plugin
from disco.types.application import InteractionType
from disco.types.message import MessageComponent, ComponentTypes, ButtonStyles, ActionRow

from KeyBot.models.keys import FreeKey

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f%z"

class KeysPlugin(Plugin):
    def load(self, ctx):

        with open("./config/interactions.yaml", "r") as raw_interaction_components:
            self.interaction_components = yaml.safe_load(raw_interaction_components)['components']

        super(KeysPlugin, self).load(ctx)

    @Plugin.listen("InteractionCreate", conditional=lambda e: e.type == InteractionType.APPLICATION_COMMAND and e.data.name == "add-key")
    def add_key_command(self, event):
        try:
            event.reply(type=9, modal=self.interaction_components['add_keys_modal'])
        except Exception as e:
            pass

    @Plugin.listen("InteractionCreate", conditional=lambda e: e.type == InteractionType.MODAL_SUBMIT and e.data.custom_id == "add_key")
    def add_key_modal_submit(self, event):

        key = None
        title = None
        platform = None

        for field in event.interaction.data.components:
            match field.components[0].custom_id:
                case 'key':
                    key = field.components[0].value
                case 'title':
                    title = field.components[0].value
                case 'platform':
                    platform = field.components[0].value

        db_key = FreeKey.create(title=title,
                       platform=platform,
                       key=key,
                       submitter=event.member.id,
                       submitted_at=datetime.now(UTC_TIMEZONE)
                )

        message_content = f"**{title}**: `{platform}`"

        button = MessageComponent()
        button.type = ComponentTypes.BUTTON
        button.style = ButtonStyles.SUCCESS
        button.label = "Claim"
        button.custom_id = f"claim_key_{db_key.id}"

        action_row = ActionRow()
        action_row.add_component(button)

        message = self.client.api.channels_messages_create(os.environ.get("FREE_KEYS_CHANNEL"), message_content,
                                                           components=[action_row.to_dict()])

        db_key.message = f"{event.guild.id}/{message.channel.id}/{message.id}"
        db_key.save()

        event.reply(type=4, content="🔑 Key Submitted.", flags=(1 << 6))

    @Plugin.listen("InteractionCreate", conditional=lambda e: e.type == InteractionType.APPLICATION_COMMAND and e.data.name == "Get Key Info")
    def get_key_info(self, event):
        to_check_for = f"{event.guild.id}/{event.channel.id}/{event.data.target_id}"
        db_key = FreeKey.get_or_none(message=to_check_for)

        if not db_key:
            return event.reply(type=4, content="ERROR: `❌ This message does not correspond to a key I can give away. ❌`", flags=(1 << 6))

        message = (f"## [Information For Key `{db_key.id}`](https://discord.com/channels/{to_check_for})"
                   "\n### Title"
                   f"\n{db_key.title}"
                   "\n### Platform"
                   f"\n{db_key.platform}"
                   "\n### Key"
                   f"\n||{db_key.key}||"
                   "\n### Submitter"
                   f"\n<@{db_key.submitter}> (<t:{int(datetime.strptime(db_key.submitted_at, DATETIME_FORMAT).timestamp())}:F> <t:{int(datetime.strptime(db_key.submitted_at, DATETIME_FORMAT).timestamp())}:R>)")

        if db_key.claimer:
            message += f"\n### Claimed By\n<@{db_key.claimer}> (<t:{int(datetime.strptime(db_key.claimed_at, DATETIME_FORMAT).timestamp())}:F> <t:{int(datetime.strptime(db_key.claimed_at, DATETIME_FORMAT).timestamp())}:R>)"

        event.reply(type=4, content=message, flags=(1 << 6))

    @Plugin.listen("InteractionCreate", conditional=lambda e: e.type == InteractionType.MESSAGE_COMPONENT and e.data.custom_id.startswith("claim_key_"))
    def claim_key(self, event):
        key_id = int(event.data.custom_id.split("_")[-1])
        db_key = FreeKey.get(id=key_id)

        if db_key.claimer:
            return event.reply(type=4, content="ERROR: `❌ Key has already been claimed. ❌`", flags=(1 << 6))

        try:
            event.member.user.open_dm().send_message(f"### Here is your key for [{db_key.title}](https://discord.com/channels/{db_key.message})\n||{db_key.key}||")
        except Exception as e:
            return event.reply(type=4, content="ERROR: `📫 DMs not open. Unable to send key. 🔑`", flags=(1 << 6))

        db_key.claimer = event.member.user.id
        db_key.claimed_at = datetime.now(UTC_TIMEZONE)
        db_key.save()

        event.reply(type=6)

        guild_id, channel_id, message_id = db_key.message.split("/")

        message = self.client.api.channels_messages_get(channel_id, message_id)

        button = MessageComponent()
        button.type = ComponentTypes.BUTTON
        button.style = ButtonStyles.SECONDARY
        button.label = "Claimed"
        button.custom_id = f"claim_key_{db_key.id}"
        button.disabled = True

        action_row = ActionRow()
        action_row.add_component(button)

        message.edit(content=message.content, components=[action_row.to_dict()])
        return