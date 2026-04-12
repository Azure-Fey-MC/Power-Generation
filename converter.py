import os
import re
from time import sleep
from json import dump

def convert():
    pool_obj = {}
    converted = 0
    def remove_empty(list_to_empty):
        new_list = []
        for item in list_to_empty:
            if item != "":
                new_list.append(item)
        return new_list
    for file_path in os.listdir("./"):
        if re.search(r'(?!\.).*?\.(?!json)([a-z]|\d)+',file_path) and not file_path in ["roll.py","converter.py","install_and_update.py"]:
            with open(file_path,"r") as file2:
                name = re.search(r".*(?=\.)",file2.name).group(0).replace(".","/")
                file_contents = remove_empty(file2.read().split("\n"))
                for line in file_contents:
                    line_contents = line.split("=")
                    if len(line_contents) == 2:
                        powers = remove_empty(line_contents[1][1:-1].split(","))
                        for power in powers:
                            power.strip()
                            match = re.search(r'(?<=").*(?=")',power)
                            if match:
                                powers[powers.index(power)] = match.group(0)
                            else:
                                powers[powers.index(power)] = power
                        match = re.search(r'"?(pool_)?(s{1,2}|a|b|c|f)"?', line_contents[0], re.IGNORECASE)
                        if match:
                            pool_obj[re.search(r"(s{1,2})|a|b|c|f", match.group(0)).group(0)] = powers
                if pool_obj:
                    with open(name + ".json", "w") as file3:
                        print(f"[{name}] {pool_obj}")
                        dump(pool_obj, file3, indent=4)
                        os.remove(file_path)
                        converted += 1
                        file3.close()
                else:
                    print(f"{file_path} is not a valid module, skipping...")
                file2.close()
        elif file_path.endswith(".json") and not file_path in ["config.json"]:
            with open(file_path,"r") as file2:
                with open("modules/"+file_path, "w") as file3:
                    file3.write(file2.read())
                    file3.close()
                file2.close()
            os.remove(file_path)
            converted += 1

    if converted > 0:
        print(f"\n\nConverted {converted} modules")
        sleep(5)