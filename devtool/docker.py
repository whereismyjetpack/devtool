from .command import run
from .minikube import minikube_env
import click


def build_docker(cfg):
    minikube = minikube_env(cfg)
    docker_command = []
    docker_command.append("docker")
    if minikube.get("DOCKER_HOST"):
        docker_command.append(f"--host={minikube['DOCKER_HOST']}")
    if minikube.get("DOCKER_TLS_VERIFY"):
        docker_command.append(f"--tlsverify={minikube['DOCKER_TLS_VERIFY']}")
    if minikube.get("DOCKER_CERT_PATH"):
        docker_command.append(f"--tlscert={minikube['DOCKER_CERT_PATH']}/cert.pem")
        docker_command.append(f"--tlscacert={minikube['DOCKER_CERT_PATH']}/ca.pem")
        docker_command.append(f"--tlskey={minikube['DOCKER_CERT_PATH']}/key.pem")

    docker_command.append("build")
    docker_command.append("-t")
    docker_command.append(f"{cfg['docker']['image']}:{cfg['docker']['tag']}")
    docker_command.append(".")
 
    str_command = " ".join(docker_command)
    click.echo(click.style(f"Running the following Docker Command: {str_command}", fg="yellow"))

    run(docker_command, cfg)