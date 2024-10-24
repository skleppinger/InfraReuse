# Import pytest
from __future__ import annotations

from pathlib import Path

# Define a global variable to track the order of execution
execution_order = []


# Hook to modify the test collection
def pytest_collection_modifyitems(config, items):
    """This was an implied requirement (initially done by abusing the alphabetical order of the test files)
    to run the integration tests first. This was needed due to *something* not being cleaned up properly
    in the unit tests that caused the integration tests to fail.
    Making this more explicit with pytest hooks.  We also may want to use this interface to speed up p2 tests.
    """
    formatted_items = "\n".join([f"{item.name} - {item.fspath}" for item in items])
    print(formatted_items)


# Hook to execute before running each test
def pytest_runtest_setup(item):
    pass


# Hook to execute each test
def pytest_runtest_call(item):
    execution_order.append(item.name)


# Hook to execute after all tests have been run
def pytest_sessionfinish(session, exitstatus):
    formatted_execution_order = "\n".join(execution_order)
    print(f"\nTest Execution Order: {formatted_execution_order}")
