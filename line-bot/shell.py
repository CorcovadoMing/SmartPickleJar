__author__ = 'Ming'

import subprocess


def shell_command(data): # data is an array
    args = [str(i) for i in data]
    p = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = p.communicate()
    return out, err
