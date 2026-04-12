try:
    import os

    if os.path.exists('.git'):
        os.system('git pull')
    else:
        os.system('git clone https://github.com/Azure-Fey-MC/Power-Generation.git')
        repo = os.listdir('Power-Generation')
        for item in repo:
            os.rename('Power-Generation/'+item, item)
        os.rmdir('Power-Generation/')

    import roll

    roll.init()
except Exception as e:
    print(e)
    with open("crash.log", "w") as f:
        f.write(str(e))