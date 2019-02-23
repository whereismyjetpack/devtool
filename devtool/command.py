import subprocess


def check_output(command):
    try:
        subprocess.check_output(command)
        return True
    except:
        return False


def run(command, cfg):
    try:
        if cfg.get("suppressoutput", False):
            subprocess.check_output(command)
        else:
            subprocess.check_call(command)
        return True
    except subprocess.CalledProcessError:
        return False
