import os.path
from logging import WARNING

from chalicelib.logs import create_logger, delete_logger, system_logger
from chalicelib.logs.log_system import SystemLogger

valid_logger_name = "test"
log_filename = "test.log"


def test_logger_log_args_kwargs():
    """
    Test logger log with args and kwargs
    """
    args = ("test", "2")
    kwargs = {"arg1": "1", "arg2": "11"}
    system_logger.log("info", "test", "default", *args, **kwargs)


def test_system_logger_dir():
    """Test logger dir"""
    logger_dir = "./"
    system_logger.directory = logger_dir
    assert logger_dir == system_logger.directory


def test_system_add_logger():
    """
    Add a logger to the list of available loggers
    """
    system_logger.add_logger(valid_logger_name, WARNING)
    assert valid_logger_name in system_logger.loggers.keys()


def test_system_add_logger_return():
    """
    Add logger with invalid name
    """
    logger_name = 1
    system_logger.add_logger(logger_name, WARNING)
    assert logger_name not in system_logger.loggers.keys()


def test_system_add_logger_exception():
    """
    Add logger with incorrect logger level (INT)
    """
    logger_name = "test_error_level"
    system_logger.add_logger(logger_name, 1)
    assert logger_name not in system_logger.loggers.keys()


def test_delete_logger():
    """
    Delete logger created before
    """
    system_logger.delete_logger(valid_logger_name)
    assert valid_logger_name not in system_logger.loggers.keys()


def test_delete_logger_no_key():
    """
    Delete non existent logger
    """
    system_logger.delete_logger("1")


def test_add_logger_with_filename():
    """
    Add a logger to the list of available loggers
    """
    logger_name = "new_logger"
    cwd = os.path.dirname(os.path.abspath(__file__))
    system_logger.directory = cwd
    system_logger.add_logger(logger_name, WARNING, None, filename=log_filename)
    assert logger_name in system_logger.loggers.keys()


def test_create_system_logger():
    logger = SystemLogger()
    assert True


def test_create_logger_root():
    create_logger(valid_logger_name, level=WARNING)
    assert valid_logger_name in system_logger.loggers.keys()


def test_delete_logger_root():
    """
    Delete logger created before
    """
    delete_logger(valid_logger_name)
    assert valid_logger_name not in system_logger.loggers.keys()
