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
import subprocess
from helm import build_helm_command, helm_setup
from minikube import minikube_setup
from command import run, check_output
from fluxhelmrelease import build_fhr
import click
from click_default_group import DefaultGroup

cfg = build_config()


@click.group(cls=DefaultGroup, default="build", default_if_no_args=True)
def main():
    pass


@main.command()
@click.option("--lang", default="java", show_default=True, type=click.Choice(['java', 'golang']))
def init(lang):
    initialize(cfg, lang)

@main.command()
def fhr():
    build_fhr(cfg)


@main.command()
def show_config():
    print(yaml.dump(cfg, default_flow_style=False))


@main.command()
@click.option(
    "--skip-compile", default=False, is_flag=True, help="Skip compiling the software"
)
@click.option(
    "--skip-docker", default=False, is_flag=True, help="Skip Docker build phase"
)
@click.option(
    "--skip-helm", default=False, is_flag=True, help="Skip helm install phase"
)
def build(skip_compile, skip_docker, skip_helm):

    minikube = minikube_setup(cfg)

    if skip_compile:
        click.echo(click.style("Skipping Compile Phase", fg="red"))
    else:
        compile_command = cfg["compile"]["command"]
        click.echo(
            click.style(
                f"Compiling software with the following command: {compile_command}",
                fg="yellow",
            )
        )
        run(compile_command.split(), cfg)

    if skip_docker:
        click.echo(click.style("Skipping Docker Phase", fg="red"))
    else:
        click.echo(click.style("Building the Docker Container", fg="yellow"))
        docker_command = f"docker --host={minikube['DOCKER_HOST']} --tlsverify={minikube['DOCKER_TLS_VERIFY']} --tlscacert={minikube['DOCKER_CERT_PATH']}/ca.pem --tlscert={minikube['DOCKER_CERT_PATH']}/cert.pem --tlskey={minikube['DOCKER_CERT_PATH']}/key.pem build -t {cfg['docker']['image']}:{cfg['docker']['tag']} ."
        run(docker_command.split(), cfg)

    if skip_helm:
        click.echo(click.style("Skipping Helm Phase", fg="red"))
    else:
        click.echo(click.style("Installing Helm Chart", fg="yellow"))
        helm_command = build_helm_command(cfg)
        run(helm_command, cfg)


if __name__ == "__main__":
    main()
