import yaml

def load_config(config_path: str = "config/config.yaml") -> dict:
    with open(config_path, "r") as file:
        config = yaml.safe_load(file)
    print(f"Configuration loaded successfully from: {config_path}")
    return config
