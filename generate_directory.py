#!/usr/bin/env python

import glob
import os
import shutil

envs = glob.glob('envs/*yml')

for env in envs:
    newdir = os.path.basename(env.split('_')[0])
    basefile = os.path.basename(env)
    os.makedirs(newdir, exist_ok=True)
    shutil.copyfile(env, os.path.join(newdir, basefile))
    with open('template.txt', 'rt') as f, open(os.path.join(newdir, 'Dockerfile'), 'w') as w:
        for line in f:
            w.write(line.replace('<env_desc>', basefile))