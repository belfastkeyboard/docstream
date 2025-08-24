import importlib
import json


def load_configs() -> dict:
    try:
        with open('plugins.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def load_plugins() -> list:
    loaded = []
    configs = load_configs()

    for module_name, function_names in configs.items():
        module = importlib.import_module(f"plugins.{module_name}")

        for function_name in function_names:
            func = getattr(module, function_name)
            loaded.append(func)

    return loaded
