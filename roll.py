import os, random, json, discord
from discord import app_commands
from dotenv import load_dotenv
from converter import convert

# Attempt to parse files into modules
convert("./modules/")
convert()

# Load Config
with open('./config.json', "r") as f:
    config = json.load(f)
load_dotenv()

def truey_str(string):
    if string.lower() in ["true", "y", "yes", "1"]:
        return True
    else:
        return False

def list_replace(full_list, item, replacement):
    full_list[full_list.index(item)] = replacement

def format_power(namespace, power, slots=0):
    if slots > 1:
        slots_format = config['slots_format'].replace("${s}", "s").replace("${count}", str(slots))
    elif slots == 1:
        slots_format = config['slots_format'].replace("${count}", str(slots))
    else:
        slots_format = ""
    formatted = config['power_format'].replace("${power}", power).replace("${namespace}", namespace).replace("${slots}", slots_format)
    return formatted.strip()

# Create pool of powers
def build_pool():
    pools = {rank: list(powers) for rank, powers in config['misc_powers'].items()}
    modules = list(config['modules'])

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
                        list_replace(module_pool[rank], power, format_power(module, power))
                    pools[rank] += module_pool[rank]

    pool = []
    for rank in pools:
        pools[rank] *= config['weights'][rank]
        pool += pools[rank]
    return pool

# Discord bot setup
intents = discord.Intents.default()
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

@tree.command(name="roll", description="Roll a set of powers to pick from.")
@app_commands.describe(rolls="How many powers to roll (defaults to standard roll count if left blank)")
async def roll(interaction: discord.Interaction, rolls: int = 5):
    pool = build_pool()

    # Generate power choices
    def replication_slots():
        power_gen = random.choice(pool)
        if power_gen == format_power("heroes", "Ability Replication"):
            while power_gen in pool:
                pool.remove(power_gen)
            slot_gen = random.choice([1] * 15 + [2, 2, 3, 4, 5])
            power_gen = format_power("heroes", "Ability Replication", slot_gen)
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

    # User inputs (now handled as slash command arguments)
    # rolls: int = 5  →  defaults to 5, or user can pass a custom value

    # Print everything
    message = "Pick one of the following powers:\n" + "\n".join(generated)
    await interaction.response.send_message(message)

@client.event
async def on_ready():
    await tree.sync()
    print(f"Logged in as {client.user}")

client.run(os.getenv('DISCORD_TOKEN'))