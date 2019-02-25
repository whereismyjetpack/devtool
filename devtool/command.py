import subprocess


def check_output(command):
    # subprocess.check_output(command, stderr=subprocess.STDOUT)
    try:
        subprocess.check_output(command, stderr=subprocess.STDOUT)
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
