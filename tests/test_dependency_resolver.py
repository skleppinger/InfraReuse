from src.dependency_resolver import DependencyResolver, ResolveByNameAndType, ResolveByName, ResolveByType
from typing import Any  
import pytest
from src.custom_exceptions import DependencyInjectionError

@pytest.fixture
def resolver():
    return DependencyResolver()

class ObjectB:
    def __init__(self, str_arg: str, **kwargs: Any):
        self.str_arg = str_arg

    def complete(self):
        return True

class ObjectC:
    def __init__(self, int_arg: int, **kwargs: Any):
        self.int_arg = int_arg

    def complete(self):
        return True

class ObjectA:
    def __init__(self, b: ObjectB, c: ObjectC, **kwargs: Any):
        self.b = b
        self.c = c
    
    def complete(self):
        return True

class ObjectD:
    def __init__(self, a: ObjectA, float_arg: float, **kwargs: Any):
        self.float_arg = float_arg

    def complete(self):
        return True
    
class ObjectSubclass(ObjectD):
    def __init__(self, object_e_unique_param: str, a: ObjectA, float_arg: float, **kwargs: Any):
        super().__init__(a, float_arg, **kwargs)
        self.object_e_unique_param = object_e_unique_param

    def complete(self):
        return True
    
class ObjectWithDefaultArg:
    def __init__(self, default_arg_var: str= "test", **kwargs: Any):
        self.default_arg_var = default_arg_var

    def complete(self):
        return True
    
class ObjectWithNoArgs:
    def __init__(self, **kwargs: Any):
        pass

    def complete(self):
        return True
    
class ObjectWithNoTypehint:
    def __init__(self, arg_without_typehint, **kwargs: Any):
        self.arg_without_typehint = arg_without_typehint

    def complete(self):
        return True

class ObjectWithUnionTypehint:
    def __init__(self, arg_with_union_typehint: str | int, **kwargs: Any):
        self.arg_with_union_typehint = arg_with_union_typehint

    def complete(self):
        return True
    
class ObjectWithOptionalTypehint:
    def __init__(self, arg_with_optional_typehint: str | None, **kwargs: Any):
        self.arg_with_optional_typehint = arg_with_optional_typehint

    def complete(self):
        return True
    
class ObjectWithListOfTypehint:
    def __init__(self, arg_with_list_of_typehint: list[str], **kwargs: Any):
        self.arg_with_list_of_typehint = arg_with_list_of_typehint

    def complete(self):
        return True

def test_str_injection(resolver: DependencyResolver):
    str_arg = "test"
    resolver.add_object(str_arg, "str_arg")
    args = resolver.resolve_object_kwargs(ObjectB, policy=ResolveByNameAndType)
    b_init = ObjectB(**args)
    assert b_init.complete()

def test_str_injection_fails(resolver: DependencyResolver):
    str_arg = "test"
    resolver.add_object(str_arg, "wrong_name")

    # should match on name, but fail on type
    with pytest.raises(DependencyInjectionError):
        args = resolver.resolve_object_kwargs(ObjectC, policy=ResolveByNameAndType)

    assert True

def test_str_injection_fails_with_no_typehint(resolver: DependencyResolver):
    str_arg = "test"
    resolver.add_object(str_arg, "str_arg")

    with pytest.raises(DependencyInjectionError):
        args = resolver.resolve_object_kwargs(ObjectWithNoTypehint, policy=ResolveByNameAndType)

def test_str_injection_fails_with_no_name(resolver: DependencyResolver):
    str_arg = "test"
    resolver.add_object(str_arg, "wrong_name")

    with pytest.raises(DependencyInjectionError):
        args = resolver.resolve_object_kwargs(ObjectWithNoTypehint, policy=ResolveByNameAndType)

def test_int_injection(resolver: DependencyResolver):
    int_arg = 1
    resolver.add_object(int_arg, "int_arg")
    args = resolver.resolve_object_kwargs(ObjectC, policy=ResolveByNameAndType)
    c_init = ObjectC(**args)
    assert c_init.complete()

def test_module_injection(resolver: DependencyResolver):
    object_b = ObjectB("test")
    object_c = ObjectC(1)
    object_a = ObjectA(object_b, object_c)
    resolver.add_object(object_a, "a")
    resolver.add_object(object_b, "ObjectB")
    resolver.add_object(object_c, "ObjectC")
    resolver.add_object(1.0, "float_arg")
    args = resolver.resolve_object_kwargs(ObjectD, policy=ResolveByNameAndType)
    d_init = ObjectD(**args)
    assert d_init.complete()

# TODO fix this to traverse MRO
def test_subclass_injection(resolver: DependencyResolver):
    object_e_unique_param = "test"
    object_b = ObjectB("test")
    object_c = ObjectC(1)
    object_a = ObjectA(object_b, object_c)
    resolver.add_object(object_a, "a")
    resolver.add_object(1.0, "float_arg")
    resolver.add_object(object_e_unique_param, "object_e_unique_param")
    args = resolver.resolve_object_kwargs(ObjectSubclass, policy=ResolveByNameAndType)
    subclass_init = ObjectSubclass(**args)
    assert subclass_init.complete()

def test_name_only_policy(resolver: DependencyResolver):
    str_arg = "test"
    resolver.add_object(str_arg, "wrong_name")
    with pytest.raises(DependencyInjectionError):
        args = resolver.resolve_object_kwargs(ObjectB, policy=ResolveByName)

    # should match on name
    resolver.add_object(str_arg, "str_arg")
    args = resolver.resolve_object_kwargs(ObjectB, policy=ResolveByName)
    b_init = ObjectB(**args)
    assert b_init.complete()

def test_type_only_policy(resolver: DependencyResolver):
    string_arg = "1"
    int_arg = 1
    resolver.add_object(string_arg, "int_arg")
    with pytest.raises(DependencyInjectionError):
        args = resolver.resolve_object_kwargs(ObjectC, policy=ResolveByType)
    
    # should match on type, even with the wrong name
    resolver.add_object(int_arg, "wrong_name")
    args = resolver.resolve_object_kwargs(ObjectC, policy=ResolveByType)
    c_init = ObjectC(**args)
    assert c_init.complete()

def test_optional_types(resolver: DependencyResolver):
    arg_with_optional_typehint = "test"
    int_arg = 1
    resolver.add_object(int_arg, "int_arg")

    args = resolver.resolve_object_kwargs(ObjectWithOptionalTypehint, policy=ResolveByNameAndType)
    with_optional_typehint_init = ObjectWithOptionalTypehint(**args)
    assert with_optional_typehint_init.complete()
    assert with_optional_typehint_init.arg_with_optional_typehint == None

    resolver.add_object(arg_with_optional_typehint, "arg_with_optional_typehint")
    args = resolver.resolve_object_kwargs(ObjectWithOptionalTypehint, policy=ResolveByNameAndType)
    with_optional_typehint_init = ObjectWithOptionalTypehint(**args)
    assert with_optional_typehint_init.complete()
    assert with_optional_typehint_init.arg_with_optional_typehint == arg_with_optional_typehint