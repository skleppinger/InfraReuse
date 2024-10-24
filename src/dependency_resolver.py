
from typing import Any, Dict

class Policy:
    """Base class for all resolution policies."""
    def __init__(self, 
                 available_objects: dict[str, Any],
                 subclass_ok: bool = True,
                 **kwargs):
        self.available_objects = available_objects
        self.subclass_ok = subclass_ok
        self.kwargs = kwargs

    def resolve(self, arg_name: str, arg_type: type):
        pass

class ResolveByType(Policy):
    """Resolve by type."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def resolve(self, arg_name: str, arg_type: type):
        for obj in self.available_objects.values():
            if self.subclass_ok and issubclass(obj, arg_type):
                return obj
            if isinstance(obj, arg_type):
                return obj
        raise KeyError(f"No object of type {arg_type} found")

class ResolveByName(Policy):
    """Resolve by name."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def resolve(self, arg_name: str, arg_type: type):
        return self.available_objects[arg_name]

class ResolveByNameAndType(Policy):
    """Resolve by name and type."""
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def resolve(self, arg_name: str, arg_type: type):
        return self.available_objects[arg_name]


class DependencyResolver:
    def __init__(self):
        self._object_bag = {}

    def resolve(self):
        pass

    def resolve_object_args(self, object_class: type, skip_args: tuple[str] = (), policy: Policy = ResolveByNameAndType, subclass_ok: bool = True):
        """
        Resolve the arguments of an object.

        skip_args: tuple[str] - are the arguments that should not be resolved (usually the args that are passed in from the config).

        """
        args = {}
        for arg_name, arg_value in object_class.__init__.__code__.co_varnames:
            if arg_name in skip_args:
                args[arg_name] = arg_value
            else:
                arg_type = object_class.__init__.__annotations__[arg_name]
                args[arg_name] = policy(subclass_ok=subclass_ok, available_objects=self._object_bag).resolve(arg_name=arg_name, arg_type=arg_type)
        return args

    def add_object(self, object_instance: Any, name: str):
        self._object_bag[name] = object_instance
