# Created in June 15, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice repository definition module.

Defines the repository interface along with patterns applied.
Repository Layer gives you additional level of abstraction over data access.
"""

from abc import ABC, abstractmethod
from typing import List

from sqlalchemy.orm import sessionmaker

import chalicelib.core as core


class Repository(ABC, metaclass=core.context_class):
    """
    Abstract repository interface reference.

    Every repository should extend from this template component,
    there's a base repository implementation to work with (even with
    custom repositories of course).

    Keep in mind that transactions/sessions need to be handled
    in this layer with repositories business logic. Repositories should
    be DDD-oriented (Domain Driven Design in software engineering terms).
    """

    PATTERN = "rds"
    AMPERSAND = "&"

    @property
    def client(self) -> sessionmaker:
        return self.__client

    @client.setter
    def client(self, value):
        self.__client = value

    def __init__(self) -> None:
        client = None

        try:
            # Core database clients is optimized only for the first time checking clients.
            # So no worries about creating different client instances.

            client = core.ClientPool.get_client(pattern=self.PATTERN)
        except Exception:
            client = None

        self.client = client

    # Base generic operations for working with common repositories


# MySQL Translator or common shared features to use with
from chalicelib.repositories.mysql_repository import BaseRepository
from chalicelib.repositories.mysql_statement import MySQLStatement
from chalicelib.repositories.mysql_translator import mysql_translator
