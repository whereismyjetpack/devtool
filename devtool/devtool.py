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
from helm import build_helm_command, helm_setup
from minikube import minikube_setup
from command import run, check_output
from fluxhelmrelease import build_fhr
import click
from click_default_group import DefaultGroup

cfg = build_config()

@click.group(cls=DefaultGroup, default='build', default_if_no_args=True)
def main():
    pass

@main.command()
def init():
    print("init")

@main.command()
def fhr():
    build_fhr(cfg)

@main.command()
def show_config():
    print(yaml.dump(cfg, default_flow_style=False))

@main.command()
@click.option("--skip-compile", default=False, is_flag=True, help="Skip compiling the software")
@click.option("--skip-docker", default=False, is_flag=True, help="Skip Docker build phase")
@click.option("--skip-helm", default=False, is_flag=True, help="Skip helm install phase")
def build(skip_compile, skip_docker, skip_helm):

    minikube = minikube_setup(cfg)

    if skip_compile:
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

    if skip_docker:
        print(colored("Skipping Docker Phase", "red"))
    else:
        # TODO set defaults on docker vars if minikube doesn't provide them. .get(foo, bar)
        print(colored(f"Building the docker container", "yellow", attrs=["bold"]))
        docker_command = f"docker --host={minikube['DOCKER_HOST']} --tlsverify={minikube['DOCKER_TLS_VERIFY']} --tlscacert={minikube['DOCKER_CERT_PATH']}/ca.pem --tlscert={minikube['DOCKER_CERT_PATH']}/cert.pem --tlskey={minikube['DOCKER_CERT_PATH']}/key.pem build -t {cfg['docker']['image']}:{cfg['docker']['tag']} ."
        run(docker_command.split(), cfg)

    if skip_helm:
        print(colored("Skipping Helm Phase", "red"))
    else:
        print(colored(f"Installing helm chart", "yellow", attrs=["bold"]))
        helm_command = build_helm_command(cfg)
        run(helm_command, cfg)



if __name__ == "__main__":
    main()
