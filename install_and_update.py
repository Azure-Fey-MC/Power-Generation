import traceback

try:
    import os, subprocess, platform, re

    operating_system = platform.system()
    print(f"Running on {operating_system}")

    git_folder = "./.git/"
    repo_folder = "./Power-Generation/"
    root_folder = "./"
    if operating_system == "Windows":
        try:
            has_git = re.search(r"git version (\d+\.){2}\d+", str(subprocess.check_output("git --version".split(" "))))
        except Exception as e:
            has_git = False
        if not has_git:
            subprocess.run("winget install --id Git.Git -e --source winget".split(" "))
        git_folder.replace("/", "\\")
        repo_folder.replace("/", "\\")
        root_folder.replace("/", "\\")
    if os.path.exists(git_folder[:-1]) and os.path.isfile(git_folder[:-1]):
        os.remove(git_folder[:-1])
    if os.path.exists(git_folder):
        subprocess.run('git pull'.split(" "))
    else:
        subprocess.run('git clone https://github.com/Azure-Fey-MC/Power-Generation.git'.split(" "))
        repo = os.listdir(repo_folder)
        for item in repo:
            if operating_system == "Windows":
                subprocess.run(f"move /y {repo_folder}{item} {root_folder}{item}".split(" "))
            else:
                subprocess.run(f"mv -f {repo_folder}{item} {root_folder}{item}".split(" "))
        os.rmdir(repo_folder)

    import roll

    roll.init()
except Exception as e:
    print(e)
    with open("crash.log", "w") as f:
        f.write(str(e)+"\n")
        f.close()
    with open("crash.log", "a") as f:
        f.write(traceback.format_exc())