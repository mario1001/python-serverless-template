from abc import ABC, abstractmethod
from typing import List

import chalicelib.core as core
from chalicelib.domain.models import MySQL
from sqlalchemy.orm.session import sessionmaker


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

    @abstractmethod
    def find_entities(self) -> List[MySQL]:
        """
        Abstract method for getting a list of entities
        and filtering by abstract parameters (not defined here,
        those would be on each implementation).

        :return: List of DaaS domain MySQL objects
        :rtype: List[MySQL]
        """

    @abstractmethod
    def find_by_id(self) -> MySQL:
        """
        Abstract method for getting an entity by
        its primary key.

        :return: The entity found in database
        :rtype: MySQL
        """

    @abstractmethod
    def create_entity(self) -> MySQL:
        """
        Abstract method for creating a new entity.

        It's intended to be only for creation firstly,
        but could be implemented with a modification request
        (letting insert/updates in the end).

        :return: The entity created/updated
        :rtype: MySQL
        """

    @abstractmethod
    def create_entities(self, entities: List[MySQL]) -> List[MySQL]:
        """
        Abstract method for creating a bunch of entities.

        Entities should be domain model concepts or ID instances
        at least (session could merge these values).

        It's intended to be only for creation firstly,
        but could be implemented with a modification request
        (letting insert/updates in the end).

        :param entities: List of entities to save
        :type entities: List[MySQL]

        :return: List of saved entities (with autovalues generated)
        :rtype: List[MySQL]
        """

    @abstractmethod
    def update_entity(self) -> MySQL:
        """
        Abstract method for entity updates.

        Not allowing new creations here,
        it's only reserved for update ones.

        :return: The entity updated
        :rtype: MySQL
        """

    @abstractmethod
    def update_entities(self, entities: List[MySQL]) -> List[MySQL]:
        """
        Abstract method for update a bunch of entities.

        It's intended to be only for update only,
        without the complex way for checking every type.

        This depends on the implementation for each database selected.

        :return: The entity created/updated
        :rtype: MySQL
        """