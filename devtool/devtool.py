"""
Usage:
  devtool  [options]
  devtool show-config
  devtool fhr
  devtool init

Options:
  --skip-compile                      Skip Compile
  --skip-docker                       Skip Docker
  --skip-helm                         Skip Helm
  --suppress-output
"""
from __future__ import absolute_import
import collections
from config import build_config
from initialize import initialize
import re
import os
import sys
import json
import yaml
import uuid
from termcolor import colored, cprint
import subprocess
from docopt import docopt
from helm import build_helm_command, helm_setup
from minikube import minikube_setup
from command import run
from command import check_output
from fluxhelmrelease import build_fhr


def parse_args():
    arguments = docopt(__doc__, version="0.0.1")
    return arguments

def main():
    arguments = parse_args()
    cfg = build_config(arguments)
    minikube = minikube_setup(cfg)

    helm_setup(cfg)

    if arguments["show-config"]:
        print(yaml.dump(cfg, default_flow_style=False))
        sys.exit(0)

    if arguments["fhr"]:
        print(build_fhr(cfg))
        sys.exit(0)

    if arguments["init"]:
        initialize(cfg)
        sys.exit(0)


    if cfg["skip"]["compile"]:
        print(colored("Skipping Compile Phase", "red"))
    else:
        compile_command = cfg["compile"]["command"]
        print(
            colored(
                f"Compiling software with the following command: {compile_command}",
                "yellow",
                attrs=["bold"],
            )
        )
        run(compile_command.split(), cfg)

    if cfg["skip"]["docker"]:
        print(colored("Skipping Docker Phase", "red"))
    else:
        # TODO set defaults on docker vars if minikube doesn't provide them. .get(foo, bar)
        print(colored(f"Building the docker container", "yellow", attrs=["bold"]))
        docker_command = f"docker --host={minikube['DOCKER_HOST']} --tlsverify={minikube['DOCKER_TLS_VERIFY']} --tlscacert={minikube['DOCKER_CERT_PATH']}/ca.pem --tlscert={minikube['DOCKER_CERT_PATH']}/cert.pem --tlskey={minikube['DOCKER_CERT_PATH']}/key.pem build -t {cfg['docker']['image']}:{cfg['docker']['tag']} ."
        run(docker_command.split(), cfg)

    if cfg["skip"]["helm"]:
        print(colored("Skipping Helm Phase", "red"))
    else:
        print(colored(f"Installing helm chart", "yellow", attrs=["bold"]))
        helm_command = build_helm_command(cfg)
        run(helm_command, cfg)


if __name__ == "__main__":
    main()
