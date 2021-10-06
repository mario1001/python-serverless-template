# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice with functions for customizing and creating logs.

System logger would be raised when runtime in this software, logs could be
added along with its configurations in this module.

This module should include functionality related to audit files integrated with the project, as many of
the functions needed.

Auditory files maybe is also moved into DynamoDB, this module should contain that part also.
"""

import logging
from logging import Logger

from chalicelib.logs.log_system import SystemLogger

system_logger = SystemLogger()


def create_logger(
    name: str,
    format: str = None,
    filename: str = None,
    level: int = logging.WARNING,
) -> Logger:
    """Create a new logger with specific configuration.

    :param name: Logger name
    :type name: str
    :param format: Logger custom format, defaults to None
    :type format: str, optional
    :param filename: Logger filename file handler, defaults to None
    :type filename: str, optional
    :param level: Logging level associated (should be valid in logger terms), defaults to logging.WARNING
    :type level: int, optional
    """

    return system_logger.add_logger(name, level, format, filename)


def delete_logger(name: str) -> None:
    """
    Delete some specific logger from system.

    :param name: [description]
    :type name: str
    """

    system_logger.delete_logger(name)
