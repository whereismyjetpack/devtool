from config import build_config
from initialize import initialize
import yaml
import os
from helm import build_helm_command, helm_setup
from minikube import minikube_setup
from command import run, check_output
from fluxhelmrelease import build_fhr
import click
from click_default_group import DefaultGroup

cfg = build_config()


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
def build(skip_compile, skip_docker, skip_helm):

    minikube = minikube_setup(cfg)

    helm_setup(cfg)

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
        click.echo(
            click.style(
                f"Running the following Helm command: \n{' '.join(helm_command)}",
                fg="yellow",
            )
        )
        run(helm_command, cfg)

        click.echo("\U0001f680")


if __name__ == "__main__":
    main()
