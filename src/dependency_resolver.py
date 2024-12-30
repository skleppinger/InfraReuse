from typing import Any, GenericAlias
from types import UnionType
import inspect
from src.custom_exceptions import DependencyInjectionError


class ConfigArg:
    """An argument that is passed in from the config, to match the python signature method."""

    def __init__(
        self,
        name: str,
        annotation: type,
        default: Any = None,
        required: bool = False,
        help: str = "",
    ):
        self.name = name
        self.annotation = annotation
        self.kind = "CONFIG"
        self.default = default

    def __repr__(self):
        return f"ConfigArg(name={self.name}, annotation={self.annotation}, default={self.default})"


class Policy:
    """Base class for all resolution policies."""

    def __init__(
        self, available_objects: dict[str, Any], subclass_ok: bool = True, **kwargs
    ) -> None:
        self.available_objects = available_objects
        self.subclass_ok = subclass_ok
        self.kwargs = kwargs

    def resolve(self, arg_name: str, arg_type: type) -> Any:
        pass


class ResolveByType(Policy):
    """Resolve by type."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def resolve(self, arg_name: str, arg_type: type) -> Any:
        for obj in self.available_objects.values():
            if isinstance(obj, arg_type):
                return obj
            if inspect.isclass(obj):
                if self.subclass_ok and issubclass(obj, arg_type):
                    return obj
        return None


class ResolveByName(Policy):
    """Resolve by name."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def resolve(self, arg_name: str, arg_type: type) -> Any:
        if arg_name in self.available_objects:
            return self.available_objects[arg_name]
        return None


class ResolveByNameAndType(Policy):
    """Resolve by name and type - matches on arg name but then validates the type of the found object."""

    def __init__(self, **kwargs) -> None:
        super().__init__(**kwargs)

    def resolve(self, arg_name: str, arg_type: type) -> Any:
        """
        Things we want to account for:
        - Single types (Foo, Bar, Baz, etc...)
        - Optional types (Foo | None) - # TODO Do we handle this after the resolve?
        - Union types (Foo | Bar | Baz)
        - Subclassed types (Foo(Bar))
        - List types (list[Foo], list[Bar], list[Baz])
        - Dict types (dict[str, Foo], dict[str, Bar], dict[str, Baz]) loosely (allow different key, values)
        - Callable types (Callable[[int, str], bool]) (for coroutines)
        - Coroutine Callable types (Callable[[int, str], Coroutine[Any, Any, bool]])
        """

        if arg_name in self.available_objects:
            is_plural_type = arg_type.__class__ is UnionType
            is_generic_type = arg_type.__class__ is GenericAlias
            if (
                not is_plural_type
                and not is_generic_type
                and isinstance(self.available_objects[arg_name], arg_type)
            ):
                return self.available_objects[arg_name]

            if is_generic_type and isinstance(
                self.available_objects[arg_name], arg_type.__origin__
            ):
                # Mostly a check for dicts with typehinted keys and values
                # if len(arg_type.__args__) == 2 and isinstance(self.available_objects[arg_name], dict):
                # TODO check if the keys and values are the correct types - needs to work with Union types
                return self.available_objects[arg_name]

            if is_plural_type:
                if type(self.available_objects[arg_name]) in arg_type.__args__:
                    return self.available_objects[arg_name]

            if self.subclass_ok and issubclass(
                self.available_objects[arg_name], arg_type
            ):
                # TODO fix this is brittle - breaks when self.available_objects[arg_name] isn't a class
                return self.available_objects[arg_name]

        return None


class DependencyResolver:  # Todo make a singleton?
    def __init__(self):
        self._object_bag: dict[str, Any] = {"_resolver": self}

    def resolve(self):
        pass

    def resolve_object_kwargs(
        self,
        object: type,
        skip_args: tuple[str] = (),
        policy: Policy = ResolveByNameAndType,
        subclass_ok: bool = True,
        additional_objects: dict[str, Any] = {},
    ):
        """
        Resolve the arguments of an object.

        skip_args: tuple[str] - are the arguments that should not be resolved (usually the args that are passed in from the config).
        policy

        """
        kwargs = {}
        signature = inspect.signature(object)
        to_resolve = []

        available_objects = self._object_bag.copy()
        available_objects.update(additional_objects)

        config = getattr(object, "CONFIG", {})
        config = config.model_fields if config else {}
        config_req = []
        for config_arg in config.items():
            # todo default factory
            config_arg = ConfigArg(
                name=config_arg[0],
                annotation=config_arg[1].annotation,
                default=config_arg[1].default,
                required=config_arg[1].is_required,
                help=config_arg[1].description or config_arg[0],
            )
            config_req.append(config_arg)

        all_params = list(signature.parameters.values())
        all_params.extend(config_req)

        for param in all_params:  # How to get parent classes args/kwargs?
            if param.name in skip_args:
                continue
            if param.kind in (
                inspect.Parameter.VAR_KEYWORD,
                inspect.Parameter.VAR_POSITIONAL,
            ):
                continue  # TODO handle kwargs in the future, and args
            if param.annotation == self.__class__:
                # Only resolve the resolver once, it's a singleton
                kwargs[param.name] = self
                continue

            # check if policy can find the value
            value = policy(
                subclass_ok=subclass_ok, available_objects=available_objects
            ).resolve(arg_name=param.name, arg_type=param.annotation)
            if value is not None:
                kwargs[param.name] = value
            else:
                to_resolve.append(param)

            # TODO in future, resolve union types and list of type x

        for param in to_resolve:
            if param.default != inspect._empty:
                kwargs[param.name] = param.default
            # check if None is in the union type
            elif (
                hasattr(param.annotation, "__class__")
                and param.annotation.__class__ is UnionType
            ):
                if type(None) in param.annotation.__args__:
                    kwargs[param.name] = None
            else:
                raise DependencyInjectionError(
                    f"No value provided for required argument {param.name}, unable to resolve {object.__name__}"
                )

        return kwargs

    def add_object(self, object_instance: Any, name: str):
        self._object_bag[name] = object_instance
