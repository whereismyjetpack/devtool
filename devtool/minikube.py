from .command import check_output
from .command import run
import subprocess
import click


def minikube_env(cfg):
    minikube = {}

    env = "minikube docker-env".split()
    try:
        docker_env = subprocess.check_output(env).split()
    except subprocess.CalledProcessError:
        click.echo(click.style(f"minikube docker-env failed. using local docker daemon", fg="red"))
        docker_env = []

    for item in docker_env:
        if "DOCKER" in item.decode("utf-8"):
            k, v = item.decode("utf-8").split("=")
            minikube[k] = str(v.strip('"'))

    return minikube


def minikube_setup(cfg):
    """
    Starts minikube if not started
    """
    minikube = {}
    minikube_memory = cfg["minikube"]["memory"]
    minikube_cpu = cfg["minikube"]["cpu"]

    if not check_output("minikube status".split()):
        click.echo(click.style("Starting Minikube...", fg="yellow"))
        cmd = "minikube start --memory %s --cpus %s" % (minikube_memory, minikube_cpu)
        run(cmd.split(), cfg)


    current_context = subprocess.check_output(
        "kubectl config current-context".split()
    ).strip()

    if current_context.decode("utf-8") != "minikube":
        click.echo(click.style("Setting kubectl context to minikube", fg="yellow"))
        run("kubectl config use-context minikube".split(), cfg)

    return minikube
