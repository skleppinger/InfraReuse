from src.dependency_resolver import DependencyResolver, ResolveByNameAndType, ResolveByName, ResolveByType
from typing import Any  
import pytest

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

def test_str_injection(resolver: DependencyResolver):
    str_arg = "test"
    resolver.add_object(str_arg, "str_arg")
    args = resolver.resolve_object_args(ObjectB, policy=ResolveByNameAndType)
    b_init = ObjectB(**args)
    assert b_init.complete()

def test_str_injection_fails(resolver: DependencyResolver):
    str_arg = "test"
    resolver.add_object(str_arg, "wrong_name")

    # should match on name, but fail on type
    args = resolver.resolve_object_args(ObjectC, policy=ResolveByNameAndType())
    with pytest.raises(KeyError):
        # args should be empty
        ObjectB(**args)

