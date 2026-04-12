try:
    import os, subprocess, platform

    operating_system = platform.system()
    print(f"Running on {operating_system}")

    git_folder = "./.git/"
    repo_folder = "./Power-Generation/"
    root_folder = "./"
    if operating_system == "Windows":
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
            subprocess.run(f"mv -f {repo_folder}{item} {root_folder}{item}".split(" "))
        os.rmdir(repo_folder)

    import roll

    roll.init()
except Exception as e:
    print(e)
    with open("crash.log", "w") as f:
        f.write(str(e))