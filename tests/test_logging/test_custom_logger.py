from src.logging.custom_logger import create_file_handler


def test_create_file_handler():
    handler = create_file_handler("test.log")
    assert handler is not None


def test_create_file_handler_with_rotation():
    handler = create_file_handler("test.log", rotate_file_logs=True)
    assert handler is not None
