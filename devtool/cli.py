from .config import build_config
from .initialize import initialize
import yaml
import os
from .helm import build_helm_command, helm_setup
from .minikube import minikube_setup, minikube_env
from .command import run, check_output
from .fluxhelmrelease import build_fhr
import click
from click_default_group import DefaultGroup

cfg = build_config()
if cfg["emoji"]:
    from .emoji import positive, skip
else:
    from .emoji import nopositive as positive
    from .emoji import noskip as skip


@click.group(cls=DefaultGroup, default="build", default_if_no_args=True)
@click.version_option(version="0.0.1")
def main():
    pass


@main.command()
@click.option(
    "--lang", default="java", show_default=True, type=click.Choice(["java", "golang"])
)
def init(lang):
    initialize(cfg, lang)


_, current_folder_name = os.path.split(os.getcwd())


@main.command()
def setup():
    minikube_setup(cfg)
    helm_setup(cfg)


@main.command()
@click.option("--write-file", "-w", is_flag=True, default=False)
@click.option("--project-name", prompt=True, default=current_folder_name)
@click.option("--environment-name", prompt=True, default="prod")
@click.option("--helm-repo-url", prompt=True, default=cfg["helm"]["repo"]["url"])
@click.option("--chart-name", prompt=True, default=cfg["helm"]["chart"])
def fhr(write_file, project_name, environment_name, helm_repo_url, chart_name):
    build_fhr(
        cfg, write_file, project_name, environment_name, helm_repo_url, chart_name
    )


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
@click.option(
    "--skip-setup", default=False, is_flag=True, help="Skip minikube/kubectl setup"
)
@click.option(
    "--suppress-output",
    default=False,
    is_flag=True,
    help="Suppress subprocess commands output",
)
def build(skip_compile, skip_docker, skip_helm, skip_setup, suppress_output):

    if cfg["skip"]["helm"]:
        skip_helm = True
    if cfg["skip"]["docker"]:
        skip_docker = True
    if cfg["skip"]["compile"]:
        skip_compile = True
    if cfg["skip"]["setup"]:
        skip_setup = True
    if suppress_output:
        cfg["suppressoutput"] = True

    if skip_setup:
        click.echo(click.style(f"{skip}Skipping Minikube/Helm setup\n", fg="red"))
    else:
        minikube = minikube_setup(cfg)
        helm_setup(cfg)

    if skip_compile:
        click.echo(click.style(f"{skip}Skipping Compile Phase\n", fg="red"))
    else:
        compile_command = cfg["compile"]["command"]
        click.echo(
            click.style(
                f"Compiling software with the following command: {compile_command}\n",
                fg="yellow",
            )
        )
        run(compile_command.split(), cfg)

    if skip_docker:
        click.echo(click.style(f"{skip}Skipping Docker Phase\n", fg="red"))
    else:
        click.echo(click.style("Building the Docker Container\n", fg="yellow"))
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
        click.echo(
            click.style(
                f"Running the following docker command: {str_command}", fg="yellow"
            )
        )
        run(docker_command, cfg)

    if skip_helm:
        click.echo(click.style(f"{skip}Skipping Helm Phase\n", fg="red"))
    else:
        click.echo(click.style("Installing Helm Chart\n", fg="yellow"))
        helm_command = build_helm_command(cfg)
        click.echo(
            click.style(
                f"Running the following Helm command: \n{' '.join(helm_command)}",
                fg="yellow",
            )
        )
        run(helm_command, cfg)

    click.echo(positive())


if __name__ == "__main__":
    main()
