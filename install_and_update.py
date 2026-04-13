import traceback

try:
    import os, subprocess, platform, re

    operating_system = platform.system()
    print(f"Running on {operating_system}")

    git_folder = "./.git/"
    repo_folder = "./Power-Generation/"
    root_folder = "./"
    try:
        has_git = re.search(r"git version (\d+\.){2}\d+", str(subprocess.check_output("git --version".split(" "))))
    except FileNotFoundError as e:
        has_git = False
    if not has_git:
        install_git=input("Git not found but is required, do you want to install git? (script will close if you decline) (y/n)")
        if install_git.lower()=="y":
            if operating_system == "Windows":
                subprocess.run("winget install --id Git.Git -e --source winget".split(" "))
            elif operating_system == "Darwin":
                subprocess.run('/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"'.split(" "))
                subprocess.run("brew install git".split(" "))
            elif platform.freedesktop_os_release()["ID_LIKE"].__contains__("ubuntu") or platform.freedesktop_os_release()["ID_LIKE"].__contains__("debian"):
                subprocess.run("sudo apt install git -y".split(" "))
            elif platform.freedesktop_os_release()["ID_LIKE"].__contains__("fedora"):
                try:
                    subprocess.run("sudo dnf install git -y".split(" "))
                except Exception as e:
                    print('Package manager "dnf" not found, please install git yourself')
            elif platform.freedesktop_os_release()["ID_LIKE"].__contains__("arch"):
                subprocess.run("sudo pacman -S git".split(" "))
            else:
                print("Package manager could not be determined, please install git yourself")
        else:
            raise FileNotFoundError("Unable to continue without git, use roll.py instead. (Automatic updates will not happen)")
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

def init():
    print("Running install script from external source")