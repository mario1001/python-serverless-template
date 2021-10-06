# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Main functions for customizing and creating logs.

What contains this package? It's designed for managing loggers and
handlers (from logging Python module).
"""

from __future__ import annotations

import logging
import os
from logging import Formatter, Logger
from typing import Any, Union


class SystemLogger(object):
    """
    System Logger designed for supplying auditory issues.

    Auditory operations could be handled by this class also, along with
    logs in different file types.

    Log files would be created in this package (files directory) if not specified
    any external service (or some platform designed to handle these files).

    Why external service for saving log files? This could be pretty great for lambda
    design patterns, this type of architecture is serverless and raised in some type of container,
    it does not make sense to save files in those environments.
    """

    AVAILABLE_LOGGER_TYPES = [
        logging.DEBUG,
        logging.INFO,
        logging.WARNING,
        logging.CRITICAL,
        logging.FATAL,
        logging.WARN,
        logging.ERROR,
    ]

    # System logger default formatter with some simple one (can be customed by overriding this class attribute)
    FORMAT = "%(asctime)s %(levelname)s %(message)s"

    DEFAULT_LOGGER_NAME = "default"
    DEFAULT_DIRECTORY = "./logs"

    LOGGER_LEVEL_OS = "LOGGER_LEVEL"

    @property
    def loggers(self):
        return self.__loggers

    @loggers.setter
    def loggers(self, value):
        self.__loggers = value

    @property
    def directory(self):
        return self.__directory

    @directory.setter
    def directory(self, value):
        self.__directory = value

    def __init__(self, directory: str = None) -> SystemLogger:
        """
        Creates a new system logger instance.

        It will create custom service depending on the service type introduced.
        Using Composite design pattern here just as a note.

        :param directory: Default directory to save logs
        :type directory: str

        :param service: Service that this log system is going to use
        :type service: :class: `models.service.Service`

        :return: :class: `logs.log_system.SystemLogger`
        :rtype: SystemLogger
        """

        # Create one default logger with output data information.
        self.loggers = {
            self.DEFAULT_LOGGER_NAME: self.__setup_logger(
                self.DEFAULT_LOGGER_NAME,
                level=os.getenv(self.LOGGER_LEVEL_OS, logging.WARNING),
            )
        }

        self.directory = self.DEFAULT_DIRECTORY

    def add_logger(
        self,
        name: str,
        logging_level: int = None,
        format: str = None,
        filename: str = None,
    ) -> Union[Logger, None]:
        """
        Associates a new logger with concrete name.

        This new logger can be matched to some specific file (if so,
        console output would be the default way), also providing a logging level
        should be along the logger types existing in logging module.

        :param name: Logger custom name to be identified (required)
        :type name: str

        :param logging_level: Logging level type specified (optional)
        :type logging_level: int

        :param format: Logging format to be outsourced
        :type format: str

        :param filename: File name route to create a file log
        (could be overwritten, take care of this)
        :type filename: str
        """

        if (
            not isinstance(name, str)
            or logging_level not in self.AVAILABLE_LOGGER_TYPES
        ):
            # Name should be identified and logging level should exist in logging module!
            return

        self.loggers[name] = self.__setup_logger(
            name, format, filename, logging_level
        )

    def __setup_logger(
        self,
        name: str,
        logger_format: str = None,
        filename: str = None,
        level: int = logging.WARNING,
    ) -> Logger:
        """Class custom method for creating logger instances.

        New ones would be added to the logger structure for this system logger data.
        Default output is console, format does have a default one and level should also be
        provided (warning as default one).

        Loggers should be identified with names, that's what that property is indented to be.

        :param name: logger name
        :type name: str
        :param logger_format: logger formatter format, defaults to None
        :type logger_format: str, optional
        :param filename: File name, defaults to output
        :type filename: str, optional
        :param level: logger level (must exists), defaults to logging.WARNING
        :type level: int, optional
        :return: new Logger instance created
        :rtype: Logger
        """

        if not logger_format:
            logger_format = self.FORMAT

        logger = logging.getLogger(name)

        try:
            logger.setLevel(level)
        except TypeError:
            logger.setLevel(logging.WARNING)

        if filename:
            # Setup specific logger handler
            handler = logging.FileHandler(
                os.path.join(os.path.sep, self.directory, filename)
            )
            handler.setFormatter(Formatter(logger_format))
            logger.addHandler(handler)

        return logger

    def delete_logger(self, name: str) -> None:
        """Delete specific logger with name identifier.

        Verify if that logger is created before making any operation.

        :param name: logger name
        :type name: str
        """

        if name not in self.loggers:
            return

        del self.loggers[name]

    def log(
        self,
        operation: str,
        msg: Any,
        name: str = "default",
        *args: Any,
        **kwargs: Any
    ) -> None:
        """Executes a logger operation (info, debug, error, etc) with some specific message
        along with arguments associated.

        Method or operation should always exist in logger, this function won't do
        anything if method is not attached to.

        :param name: Specific logger registered in this system logging
        :type name: str

        :param operation: Operation to be executed in logger
        :type operation: str

        :param msg: Message to log with format parameters (included)
        :type msg: Any
        """

        if name not in self.loggers or not hasattr(
            self.loggers[name], operation
        ):
            return

        parameters = [msg]
        if args:
            for parameter in args:
                parameters.append(parameter)

        if kwargs:
            for parameter in kwargs:
                parameters.append(kwargs[parameter])

        getattr(self.loggers[name], operation)(*parameters)
