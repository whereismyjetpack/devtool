import os
import subprocess

def build_helm_command(cfg):
    default_sets = [
        "secrets.OAUTH_CLIENT_SECRET=${OAUTH_CLIENT_SECRET}",
        "secrets.OAUTH_CLIENT_ID=${OAUTH_CLIENT_ID}",
        "secrets.OAUTH_JWK=${OAUTH_JWK}",
        "image.pullPolicy=IfNotPresent",
        "image.repository=%s" % cfg["docker"]["image"],
        "image.tag=%s" % cfg["docker"]["tag"],
    ]

    helm_set = default_sets + cfg["helm"]["set"]
    values_files = cfg["helm"]["valuesFiles"]
    chart_version = cfg["helm"].get("chartVersion", None)

    helm_base = "helm upgrade %s --install" % (
        cfg["helm"]["releasename"],
        # cfg["helm"]["repo"]["name"],
        # cfg["helm"]["chart"],
    )

    helm_command = helm_base.split()

    # if chart_name is a local file, use it else use the repo/chart_name
    if os.path.isdir(cfg["helm"]["chart"]):
        helm_command.append(cfg["helm"]["chart"])
    else:
        helm_command.append(f'{cfg["helm"]["repo"]["name"]}/{cfg["helm"]["chart"]}')

    if chart_version:
        helm_command.append("--version")
        helm_command.append(chart_version)
    for statement in helm_set:
        helm_command.append("--set")
        helm_command.append(statement)

    if os.path.isfile("config/local.yml"):
        values_files.append("config/local.yml")

    for f in values_files:
        helm_command.append("-f")
        helm_command.append(f)

    return helm_command


def helm_setup(cfg):
    repos = [
        f.decode("utf-8")
        for f in subprocess.check_output("helm repo list".split()).split()
    ]
    if not cfg["helm"]["repo"]["name"] in repos:
        subprocess.check_call(
            f"helm repo add {cfg['helm']['repo']['name']} {cfg['helm']['repo']['url']}".split()
        )
