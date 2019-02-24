from command import check_output
from command import run
import subprocess
import click


def minikube_setup(cfg):
    minikube = {}
    minikube_memory = cfg.get("minikube", {}).get("memory", 4096)
    minikube_cpu = cfg.get("minikube", {}).get("cpu", 1)

    if not check_output("minikube status".split()):
        click.echo(click.style("Starting Minikube...", fg="yellow"))
        cmd = "minikube start --memory %s --cpus %s" % (minikube_memory, minikube_cpu)
        run(cmd.split(), cfg)

    env = "minikube docker-env".split()
    docker_env = subprocess.check_output(env).split()
    for item in docker_env:
        if "DOCKER" in item.decode("utf-8"):
            k, v = item.decode("utf-8").split("=")
            minikube[k] = str(v.strip('"'))

    current_context = subprocess.check_output(
        "kubectl config current-context".split()
    ).strip()
    if current_context.decode("utf-8") != "minikube":
        click.echo(click.style("Setting kubectl context to minikube", fg="yellow"))
        run("kubectl config use-context minikube".split(), cfg)

    return minikube
