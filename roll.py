import os
import random, json
from time import sleep
if os.path.exists("converter.py"):
    from converter import convert

    # Attempt to parse files into modules
    convert("./modules/")
    convert()
else:
    print("It is recommended to get the converter script from https://raw.githubusercontent.com/Azure-Fey-MC/Power-Generation/refs/heads/main/converter.py")

# Load Config
with open('config.json', "r") as f:
    config = json.load(f)
    f.close()

# Create pool of powers
def truey_str(string):
    if string.lower() in ["true","y","yes","1"]:
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
pools = config['misc_powers']
pool = []
for module in config['modules']:
    if os.path.exists("modules/"+module) or os.path.exists("modules/"+module+".json"):
        if os.path.isdir("modules/"+module):
            module_group = os.listdir("modules/"+module)
            for internal_module in module_group:
                if internal_module.endswith(".json"):
                    list_replace(module_group, internal_module, module + "/" + internal_module[:-5])
                else:
                    module_group.remove(internal_module)
            config['modules'].remove(module)
            config['modules'] += module_group
        else:
            with open("modules/"+module+".json", "r") as f:
                module_pool = json.load(f)
                f.close()
            for rank in module_pool:
                for power in module_pool[rank]:
                    list_replace(module_pool[rank], power, format_power(module, power))
                pools[rank] += module_pool[rank]
    else:
        proceed_without = input(f'Invalid module "{module}". Continue without it? (y/n)\n')
        if not truey_str(proceed_without):
            raise ModuleNotFoundError("Invalid Module Given")
for rank in pools:
    pools[rank] *= config['weights'][rank]
    pool += pools[rank]

#User inputs
minutes=float(input("How many minutes do you want the script to wait after generation before closing? \n"))
rolls=input("How many times do you want to roll? (leave blank for standard roll count) \n")
if rolls == "":
    rolls = 5
else:
    rolls = int(rolls)

# Generate power choices
def replication_slots():
    power_gen = random.choice(pool)
    if power_gen == format_power("heroes", "Ability Replication"):
        while power_gen in pool:
            pool.remove(power_gen)
        slot_gen = random.choice([1]*15+[2,2,3,4,5])
        power_gen = format_power("heroes", "Ability Replication", slot_gen)
    return power_gen
generated = []
while rolls > 0:
    power_rolled=replication_slots()
    while power_rolled in pool:
        pool.remove(power_rolled)
    for namespace in config['dual_namespaces']:
        if power_rolled.__contains__(namespace) or power_rolled in config['dual_powers'] and not power_rolled.__contains__("&"):
            power_rolled = f"{power_rolled} & {replication_slots()}"
    power_rolled = f"- {power_rolled}"
    generated.append(power_rolled)
    rolls-=1

# Print everything
print("Pick one of the following powers:\n")
for power in generated:
    print(power)

#Final sleep
sleep(minutes*60)

def init():
    run = True