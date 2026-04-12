import os

if os.path.exists('.git'):
    os.system('git pull')
else:
    os.system('git clone https://github.com/Azure-Fey-MC/Power-Generation.git')

import roll

roll.convert()
roll.run()