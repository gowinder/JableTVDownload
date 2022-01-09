
from conf.config import *

saved = set()
with open(target_file, 'r') as f:
    targets = f.readlines()
    
for target in targets:
    if target not in saved:
        saved.add(target)
        with open(saved_file, 'a') as f:
            f.writelines([target])
        print('update saved file success')
    with open(target_file, 'r+') as f:
        lines = f.readlines()
        f.seek(0)
        f.truncate()
        f.writelines(lines[1:])

    print('update target file success')