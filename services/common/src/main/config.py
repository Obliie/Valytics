import yaml
import os


CONFIG_PATH = "/service-config"
SECRETS_PATH = "/run/secrets/service-secrets"


class Config:
    CONFIG = dict()

    with open(CONFIG_PATH) as config_file:
        CONFIG = yaml.safe_load(config_file)

    if os.path.exists(SECRETS_PATH):
        with open(SECRETS_PATH) as secrets_file:
            CONFIG["Secrets"] = yaml.safe_load(secrets_file)
