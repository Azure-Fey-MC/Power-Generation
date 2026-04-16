import discord
from discord import app_commands
import os, random, json, dotenv
from converter import convert

# Attempt to parse files into modules
convert("./modules/")
convert()

# Load Config
dotenv.load_dotenv()
with open('./config.json', "r") as f:
    default_config = json.load(f)
roll_category_id = int(os.getenv('ROLL_CATEGORY'))

def list_replace(full_list, item, replacement):
    full_list[full_list.index(item)] = replacement

def format_power(namespace, power, config, slots=0):
    if slots > 1:
        slots_format = config['slots_format'].replace("${s}", "s").replace("${count}", str(slots))
    elif slots == 1:
        slots_format = config['slots_format'].replace("${count}", str(slots))
    else:
        slots_format = ""
    formatted = config['power_format'].replace("${power}", power).replace("${namespace}", namespace).replace("${slots}", slots_format)
    return formatted.strip()

# Create pool of powers
def build_pool(config, force_roll=False):
    pools = {rank: list(powers) for rank, powers in config['misc_powers'].items()}
    modules = list(config['modules'])
    missing_modules = []

    for module in modules:
        if os.path.exists("./modules/" + module) or os.path.exists("./modules/" + module + ".json"):
            if os.path.isdir("modules/" + module):
                module_group = os.listdir("./modules/" + module)
                for internal_module in list(module_group):
                    if internal_module.endswith(".json"):
                        list_replace(module_group, internal_module, module + "/" + internal_module[:-5])
                    else:
                        module_group.remove(internal_module)
            else:
                with open("modules/" + module + ".json", "r") as f:
                    module_pool = json.load(f)
                for rank in module_pool:
                    for power in module_pool[rank]:
                        list_replace(module_pool[rank], power, format_power(module, power, config))
                    pools[rank] += module_pool[rank]
        else:
            missing_modules.append(module)

    # If any modules are missing and force_roll is off, return early with the missing list
    if missing_modules and not force_roll:
        return None, missing_modules

    pool = []
    for rank in pools:
        pools[rank] *= config['weights'][rank]
        pool += pools[rank]
    return pool, missing_modules

def do_roll(config, rolls=5, force_roll=False):
    # Shared roll logic used by both the slash command and the auto-roll event.
    pool, missing_modules = build_pool(config, force_roll)

    # Generate power choices
    def replication_slots():
        power_gen = random.choice(pool)
        if power_gen == format_power("heroes", "Ability Replication", config):
            while power_gen in pool:
                pool.remove(power_gen)
            slot_gen = random.choice([1] * 15 + [2, 2, 3, 4, 5])
            power_gen = format_power("heroes", "Ability Replication", config, slot_gen)
        return power_gen

    generated = []
    remaining = rolls
    while remaining > 0:
        power_rolled = replication_slots()
        while power_rolled in pool:
            pool.remove(power_rolled)
        for namespace in config['dual_namespaces']:
            if power_rolled.__contains__(namespace) or power_rolled in config['dual_powers'] and not power_rolled.__contains__("&"):
                power_rolled = f"{power_rolled} & {replication_slots()}"
        generated.append(f"- {power_rolled}")
        remaining -= 1

    return pool, missing_modules, generated

# Discord bot setup
intents = discord.Intents.default()
intents.guilds = True
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="roll", description="Roll a set of powers to pick from.")
@app_commands.describe(
    rolls="How many powers to roll (defaults to standard roll count if left blank)",
    config_file="Optional config JSON file to use instead of the default",
    force_roll="If true, continues rolling even if a module is missing (default: false)"
)
async def roll(interaction: discord.Interaction, rolls: int = 5, config_file: discord.Attachment = None, force_roll: bool = False):
    # User inputs (now handled as slash command arguments)
    # rolls: int = 5          → defaults to 5, or user can pass a custom value
    # force_roll: bool = False → if true, skips missing modules silently

    # Load uploaded config if provided, otherwise fall back to default
    if config_file is not None:
        if not config_file.filename.endswith(".json"):
            await interaction.response.send_message("Config file must be a `.json` file.", ephemeral=True)
            return
        config_bytes = await config_file.read()
        config = json.loads(config_bytes.decode("utf-8"))
    else:
        config = default_config

    pool, missing_modules, generated = do_roll(config, rolls, force_roll)

    if len(missing_modules) > 0:
        missing_list = "\n".join(f"- `{m}`" for m in missing_modules)
        await interaction.response.send_message(
            f"The following modules could not be found:\n{missing_list}\n\nUse `force_roll: True` to roll anyway without them.",
            ephemeral=True
        )
        return

    # Print everything
    message = "Pick one of the following powers:\n" + "\n".join(generated)
    await interaction.response.send_message(message)

@client.event
async def on_guild_channel_create(channel):
    # Auto-roll with default values when a channel is created in the roll category
    if isinstance(channel, discord.TextChannel) and channel.category_id == roll_category_id:
        pool, missing_modules, generated = do_roll(default_config)
        if missing_modules:
            missing_list = "\n".join(f"- `{m}`" for m in missing_modules)
            await channel.send(f"⚠️ The following modules could not be found:\n{missing_list}")
            return

        # Print everything
        message = "Pick one of the following powers:\n" + "\n".join(generated)
        await channel.send(message)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(os.getenv('DISCORD_TOKEN'))