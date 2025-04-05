import yaml
from disco.bot import Plugin
from disco.types.application import ApplicationCommandTypes
from dotenv import load_dotenv


class CorePlugin(Plugin):
    def load(self, ctx):
        load_dotenv()
        super(CorePlugin, self).load(ctx)

    @Plugin.listen('Ready')
    def on_ready(self, event):
        # Bot Startup Logging.
        self.log.info(f"Bot connected as {self.client.state.me}")

        # Register all commands globally.
        with open("./config/interactions.yaml", "r") as raw_interaction_components:
            interaction_components = yaml.safe_load(raw_interaction_components)

        to_register = []
        for global_type, global_type_commands in interaction_components['commands']['global'].items():
            if len(global_type_commands):
                self.log.info(f"Found {len(global_type_commands)} {global_type} command(s) to register...")
                for command in global_type_commands:
                    command["type"] = getattr(ApplicationCommandTypes, global_type.upper())
                    to_register.append(command)

        self.log.info(f"Attempting to register {len(to_register)} commands...")

        updated_commands = self.client.api.applications_global_commands_bulk_overwrite(to_register)
        self.log.info(f"Successfully Registered {len(updated_commands)} commands!")