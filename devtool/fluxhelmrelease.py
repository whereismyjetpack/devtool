import os
from jinja2 import Environment, FunctionLoader
import subprocess
import click
from templates import fhr


def build_fhr(cfg, wf, project_name, environment_name, helm_repo_url, chart_name):
    variables = {}
    variables["namespace"] = cfg["namespace"]


    values = subprocess.check_output(
        f"helm inspect values {cfg['helm']['repo']['name']}/{cfg['helm']['chart']}".split()
    )

    variables["values"] = values.decode("utf-8")

    env = Environment(loader=FunctionLoader(fhr))
    template = env.get_template("fhr.j2")

    # TODO fix this
    flux_automated = False

    if flux_automated:
        variables["flux_automated"] = True
    else:
        variables["flux_automated"] = False

    variables["chart_name"] = chart_name
    variables["helm_repository"] = helm_repo_url

    if environment_name == "prod":
        variables["release_name"] = project_name
    else:
        variables["release_name"] = f"{project_name}-{environment_name}"

    filename = f"{variables['release_name']}-helmrelease.yaml"

    def write_file(filename):
        f = open(filename, "w")
        print(f"writing out {filename}")
        f.write(template.render(variables))
        f.close()

    if wf:
        if os.path.isfile(filename):
            if click.confirm(f"{filename} exists, overwrite?"):
                write_file(filename)
        else:
            write_file(filename)
    else:
        click.echo(template.render(variables))
