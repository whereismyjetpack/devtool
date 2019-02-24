import os
from jinja2 import Environment, FunctionLoader
import subprocess
import click
from templates import fhr

def build_fhr(cfg, wf):
    variables = {}
    variables["namespace"] = cfg["namespace"]

    values = subprocess.check_output(
        f"helm inspect values {cfg['helm']['repo']['name']}/{cfg['helm']['chart']}".split()
    )

    variables["values"] = values.decode("utf-8")

    env = Environment(loader=FunctionLoader(fhr))
    template = env.get_template("fhr.j2")
    _, current_folder_name = os.path.split(os.getcwd())

    project_name = input(f"Project Name [{current_folder_name}]") or current_folder_name
    environment = input(f"Environment Name: ")
    chart_repo_url = (
        input(f"Repo URL [{cfg['helm']['repo']['url']}]") or cfg["helm"]["repo"]["url"]
    )
    chart_name = input(f"Chart Name [{cfg['helm']['chart']}]") or cfg["helm"]["chart"]
    flux_automated = input(f"automate?:") or False

    if flux_automated:
        variables["flux_automated"] = True
    else:
        variables["flux_automated"] = False

    variables["chart_name"] = chart_name
    variables["helm_repository"] = chart_repo_url

    if environment:
        variables["release_name"] = f"{project_name}-{environment}"
    else:
        variables["release_name"] = project_name

    filename = f"{variables['release_name']}-helmrelease.yaml"

    def write_file(filename):
        f = open(filename, "w")
        print(f"writing out {filename}")
        f.write(template.render(variables))
        f.close()

    if wf:
        if os.path.isfile(filename):
            yn = input(f"{filename} exists, overwrite? [y/n] ")
            if yn == "y":
                write_file(filename)
        else:
            write_file(filename)
    else:
        click.echo(template.render(variables))
