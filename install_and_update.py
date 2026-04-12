try:
    import os, subprocess, platform

    operating_system = platform.system()
    print(f"Running on {operating_system}")

    git_folder = "./.git/"
    repo_folder = "./Power-Generation/"
    if operating_system == "Windows":
        git_folder.replace("/", "\\")
        repo_folder.replace("/", "\\")
    if os.path.exists(git_folder):
        subprocess.run('git pull'.split(" "))
    else:
        subprocess.run('git clone https://github.com/Azure-Fey-MC/Power-Generation.git'.split(" "))
        repo = os.listdir(repo_folder)
        for item in repo:
            with open(item, "w") as f:
                with open(repo_folder+item, "r") as f2:
                    f.write(f2.read())
                    f2.close()
                f.close()
        os.rmdir(repo_folder)

    import roll

    roll.init()
except Exception as e:
    print(e)
    with open("crash.log", "w") as f:
        f.write(str(e))