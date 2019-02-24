import os
from jinja2 import Environment, FunctionLoader
import subprocess


def fhr_template(template):
    template = """
---
apiVersion: flux.weave.works/v1beta1
kind: HelmRelease
metadata:
  name: {{ release_name }}
  namespace: {{ namespace }}
  annotations:
{%- if flux_automated %}
    flux.weave.works/automated: "true"
{%- else %}
    flux.weave.works/automated: "false"
{%- endif %}
spec:
  resetValues: true
  chart:
    repository: {{ helm_repository }}
    name: {{ chart_name }}
{%- if chart_version is defined %}
    version: {{ chart_version }}
{%- endif %}
  releaseName: {{ release_name }}
  values:
    {{ values| indent(4) }}
"""

    return template


def build_fhr(cfg):
    variables = {}
    variables["namespace"] = cfg["namespace"]

    values = subprocess.check_output(
        f"helm inspect values {cfg['helm']['repo']['name']}/{cfg['helm']['chart']}".split()
    )

    variables["values"] = values.decode("utf-8")

    env = Environment(loader=FunctionLoader(fhr_template))
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

    if os.path.isfile(filename):
        yn = input(f"{filename} exists, overwrite? [y/n] ")
        if yn == "y":
            write_file(filename)
    else:
        write_file(filename)
