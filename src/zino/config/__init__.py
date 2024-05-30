from tomli import load


def read_configuration(config_file: str):
    """Loads config file into process state."""
    with open(config_file, mode="rb") as cf:
        config = load(cf)

    return config
