# Created in June 12, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice resources module.

Contains global project resources.
"""

import io
import os
import re

from configobj import ConfigObj

from chalicelib.logs import system_logger


class Resources(object):
    """
    Microservice main resources class reference.

    Contains a dictionary with the names of the service functions
    prepared. Those services are mapped with the URL endpoint
    obtained from AWS API Gateway.
    """

    LOGGERS_SECTION = "LOGGERS"
    LOGGER_LEVEL = "logger_level"

    CONFIG_PATH = "chalicelib/config.ini"

    HTTP_RESPONSE_SECTION = "HTTP_RESPONSE"
    DEFAULT_DOMAIN_URL = "default_domain_url"

    X_AUTH_TOKEN = "x-auth-token"

    def __init__(self):
        """
        Creates a resources instance with specified configuration data.
        """

        config = ConfigObj(self.substitute_env())
        self.__config = config

        # Own log module would take into consideration none or not specified values
        self.__logging_level = config[self.LOGGERS_SECTION][self.LOGGER_LEVEL]

        self.__default_url = config[self.HTTP_RESPONSE_SECTION][
            self.DEFAULT_DOMAIN_URL
        ]
        self.authentication_token = None

    # Read-only properties for config and services
    # Not allowing any external modification

    @property
    def config(self):
        return self.__config

    @property
    def logging_level(self):
        return self.__logging_level

    @property
    def get_default_url(self):
        return self.__default_url

    def substitute_env(self):
        """
        Reads the project config file, substitutes environment variables and returns a file-like
        object of the result.

        Configuration file should be saved in the main directory of this project (src as mark directory).

        Substitution maps text like "$FOO" for the environment variable "FOO".
        """

        def lookup(match):
            """Replaces a match like $FOO with the env var FOO."""

            key = match.group(2)
            if key in os.environ:
                return os.environ.get(key)

            system_logger.log(
                "info", "Config os environment var %s not set", key
            )

            return None

        pattern = re.compile(r"(\$(\w+))")
        with open(self.CONFIG_PATH, "r") as src:
            content = src.read()
            replaced = pattern.sub(lookup, content)

        return io.StringIO(replaced)


resources = Resources()
