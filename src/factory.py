import importlib


def load_classes_from_paths(class_paths: list[str]) -> list[type]:
    pass


def parse_config_for_class_paths(config: dict, verbose: bool = False) -> dict:
    pass


def load_classes(list_of_things: list[dict[str, str]]) -> list[type]:
    """Load class definitions from a list of paths, return a list of classes.

    Arguments:
        things: a list of things to load, each thing is a dict with a "module" field
        and optionally an "enabled" field.
        Managers are special, they can just be a string of the format
        "src.managers.my_manager:MyManager"
    Returns:
        list of classes

    TODO have this read in the "enabled" field and only load the enabled ones
    """
    loaded_classes = []
    for thing in list_of_things:
        try:
            if thing.get("enabled", True):
                thing_path_and_class = thing["module"]
                thing_path, class_name = thing_path_and_class.rsplit(":", 1)
                thing_module = importlib.import_module(thing_path)
                thing_class = getattr(thing_module, class_name)
                loaded_classes.append(thing_class)
            else:
                print(f"Skipping disabled class {thing_path_and_class}")
        except ImportError as e:
            raise ImportError(f"Error loading class {thing_path_and_class}: {e}")
        except Exception as e:
            raise Exception(f"Error loading class {thing_path_and_class}: {e}")

    return loaded_classes
