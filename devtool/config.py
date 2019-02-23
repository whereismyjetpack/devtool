import os
import uuid
import yaml


def mergedicts(dict1, dict2):
    for k in set(dict1.keys()).union(dict2.keys()):
        if k in dict1 and k in dict2:
            if isinstance(dict1[k], dict) and isinstance(dict2[k], dict):
                yield (k, dict(mergedicts(dict1[k], dict2[k])))
            else:
                # If one of the values is not a dict, you can't continue merging it.
                # Value from second dict overrides one in first and we move on.
                yield (k, dict2[k])
                # Alternatively, replace this with exception raiser to alert you of value conflicts
        elif k in dict1:
            yield (k, dict1[k])
        else:
            yield (k, dict2[k])


def build_config():
    defaults = get_defaults()
    cfg = {}

    def open_config_file(filename):
        with open(filename, "r") as stream:
            try:
                cfg = yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

        return cfg

    if os.path.isfile(".devtool-config.yml"):
        cfg = open_config_file(".devtool-config.yml")

    if os.path.isfile(".devtool-config.yaml"):
        cfg = open_config_file(".devtool-config.yaml")

    merged = dict(mergedicts(defaults, cfg))

    # if arguments["--skip-compile"]:
    #     merged["skip"]["compile"] = True

    # if arguments["--skip-docker"]:
    #     merged["skip"]["docker"] = True

    # if arguments["--skip-helm"]:
    #     merged["skip"]["helm"] = True

    # if arguments["--suppress-output"]:
    #     merged["suppressoutput"] = True

    return merged


def get_defaults():
    _, current_folder_name = os.path.split(os.getcwd())
    defaults = {}
    defaults["projectname"] = current_folder_name
    defaults["namespace"] = "eio-swe"
    defaults["compile"] = {}
    defaults["compile"]["command"] = "mvn clean install"
    defaults["docker"] = {}
    defaults["docker"]["image"] = current_folder_name
    defaults["docker"]["tag"] = uuid.uuid4()
    defaults["skip"] = {}
    defaults["skip"]["docker"] = False
    defaults["skip"]["helm"] = False
    defaults["skip"]["compile"] = False
    defaults["suppressoutput"] = False
    defaults["helm"] = {}
    defaults["helm"]["repo"] = {}
    defaults["helm"]["repo"]["url"] = "https://cm.qa.k8s.psu.edu"
    defaults["helm"]["repo"]["name"] = "cm"
    defaults["helm"]["releasename"] = current_folder_name + "-local"
    defaults["helm"]["valuesFiles"] = []
    defaults["helm"]["chart"] = "eio-swe-service"
    defaults["helm"]["set"] = []

    return defaults
