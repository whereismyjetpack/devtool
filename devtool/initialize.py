import os
import click
import subprocess

def initialize(cfg, lang):
    if lang == "java":
        init_java(cfg)
    elif lang == "golang":
        print("we are initializing a golang project")


def init_java(cfg):
    if not os.path.isdir("config"):
        click.echo(click.style("Creating config directory", fg="yellow"))
        os.mkdir("config")

    if not os.path.isfile("config/local.yml"):
        click.echo(click.style("creating local configuratation", fg="yellow"))
        values = subprocess.check_output(
        f"helm inspect values {cfg['helm']['repo']['name']}/{cfg['helm']['chart']}".split())
        with open("config/local.yml", "w") as f:
            f.write(values.decode("utf-8"))

    # if not os.path.isfile("Dockerfile"):
    #     click.echo(click.style("Creating a Dockerfile", fg="yellow"))
    #     with open("Dockerfile", "w") as f:


 

        


