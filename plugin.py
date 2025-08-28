import importlib
import json
from pathlib import Path


def _load_configs() -> dict:
    try:
        with open('plugins.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def load_plugins() -> dict:
    loaded = {}
    configs = _load_configs()

    if configs:
        Path('plugins').mkdir(exist_ok=True)

    for namespace, dictionary in configs.items():
        for module_name, function_names in dictionary.items():
            module = importlib.import_module(f"plugins.{module_name}")

            for function_name in function_names:
                func = getattr(module, function_name)
                functions = loaded.get(namespace, [])
                functions.append(func)
                loaded[namespace] = functions

    return loaded
