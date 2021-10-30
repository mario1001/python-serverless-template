# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template core database connection module.

Manages the database clients with singleton design pattern
applied and saved to the application context.
"""

from __future__ import annotations

import json
from typing import Dict, List

import chalicelib.core as core
import chalicelib.exceptions as exceptions
import chalicelib.resources as resources
import sqlalchemy
from chalicelib.logs import system_logger
from sqlalchemy.orm import scoped_session, sessionmaker

main_resources: resources.Resources = resources.resources


class DatabaseClient(object):
    """
    Database client class reference.

    Our problems are retailed with the introduction
    of the node concept (connection type somehow different)
    but nodes have the same client (using the same client
    in our system at least).
    """

    @property
    def node_id(self) -> str:
        return self.__node_id

    @node_id.setter
    def node_id(self, value):
        self.__node_id = value

    # Associating a database type here
    # for fast searches with pattern

    @property
    def type(self) -> str:
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def client(self) -> scoped_session:
        return self.__client

    @client.setter
    def client(self, value):
        self.__client = value

    @property
    def operations(self) -> List[str]:
        return self.__operations

    @operations.setter
    def operations(self, value):
        self.__operations = value

    def __init__(
        self,
        node_id: str,
        client: scoped_session,
        type: str,
        operations: List[str],
    ) -> None:
        self.node_id = node_id
        self.client = client
        self.type = type

        if isinstance(operations, str):
            operations = [operations]

        self.operations = operations


class ClientPool(object):
    """
    Database pool client class reference.

    Manages internally unique/single references
    attempting to the software design pattern singleton.

    Could handle several database clients with different nodes (node
    connections should be specified in config file). The configured
    clients could be accessed providing the node-type (node ID to identify).

    This way, contains the different connections mapped along the
    unique instance to work with, used by this template framework.
    """

    MYSQL_SECTION = "MYSQL"
    NODE_SECTION = "NODE-"

    DEFAULT_OPERATIONS = ["SELECT", "INSERT", "UPDATE", "DELETE"]

    """@core.classproperty
    def client_pool(cls) -> ClientPool:

        if not hasattr(cls, "pool"):
            cls.pool = ClientPool()

        return cls.pool"""

    @property
    def clients(self) -> List[DatabaseClient]:
        if not hasattr(self, "internal_clients"):
            self.internal_clients = list()

        return self.internal_clients

    def get_node_client(self, pattern: str) -> List[DatabaseClient]:
        """
        Method for getting the node database client (SQLAlchemy sessionmaker
        for creating the sessions for each transaction).

        SQLAlchemy sessions could be created with sessionmaker object,
        used for query/insert operations also.

        This method does not update (if configured new connections)
        for clients in the specific pool (use the other method, the static
        one for getting database clients).

        :param pattern: Node ID concept, Client
        type or database operations to search for in the pool
        :type pattern: str | List[str]

        :raises exceptions.NodeNotFoundException: When no having the node ID

        :return: A database client to work with
        :rtype: DatabaseClient
        """

        databases = list()
        for database_client in self.clients:
            if (
                isinstance(pattern, str)
                and (
                    pattern == database_client.type
                    or pattern in database_client.node_id
                    or pattern in database_client.operations
                )
            ) or (
                isinstance(pattern, list)
                and (
                    (
                        len(database_client.operations) == len(pattern)
                        and set(database_client.operations) == set(pattern)
                    )
                    or (
                        len(pattern) == 1
                        and pattern[0] in database_client.operations
                    )
                    or (
                        len(
                            [
                                value
                                for value in pattern
                                if value in database_client.operations
                            ]
                        )
                        == len(pattern)
                    )
                    or (
                        database_client.type in pattern
                        or database_client.node_id in pattern
                    )
                )
            ):
                databases.append(database_client)

        if databases:
            return databases

        raise exceptions.NodeNotFoundException()

    def main_node_logic(self, config_properties: dict):

        for section, properties in config_properties.items():
            if isinstance(properties, dict) and section.startswith(
                self.NODE_SECTION
            ):

                if next(
                    (
                        database_client
                        for database_client in self.clients
                        if database_client.node_id == section
                    ),
                    None,
                ):
                    continue

                # Node found, save properties
                # create an engine
                try:
                    engine = sqlalchemy.create_engine(
                        "mysql+mysqlconnector://{default_username}:{default_password}@"
                        "{default_endpoint}:{default_port}/{default_database}?charset=utf8".format(
                            **properties
                        )
                    )
                    engine.connect()

                    # create a configured "Session" class
                    session = scoped_session(
                        sessionmaker(
                            bind=engine,
                            expire_on_commit=False,
                            autoflush=False,
                            autocommit=False,
                        )
                    )

                    system_logger.log(
                        "info",
                        "[{MODULE}][{FUNCTION}]: ".format(
                            MODULE=__name__,
                            FUNCTION=self.main_node_logic.__name__,
                        )
                        + "Adding to the client pool: {}".format(
                            json.dumps(properties)
                        ),
                    )

                    self.clients.append(
                        DatabaseClient(
                            section,
                            session,
                            "rds",
                            properties.get(
                                "operations", self.DEFAULT_OPERATIONS
                            ),
                        )
                    )
                except Exception as e:

                    # Some errors when trying the SQLAlchemy creation
                    system_logger.log(
                        "warning",
                        "[{MODULE}][{FUNCTION}]: ".format(
                            MODULE=__name__,
                            FUNCTION=self.__create_connections.__name__,
                        )
                        + "Creating engine failing due to: {}".format(str(e)),
                    )

            if isinstance(properties, dict) and properties:

                # Subsection found, inspect with recursive function
                self.main_node_logic(properties)

    def inspect_nodes(self, config_properties: dict):
        return self.main_node_logic(config_properties)

    def read_nodes(self, config_properties: dict) -> List[Dict[str, str]]:
        """
        Recursive method for getting all node connections in the
        configuration file associated for this project template.

        :param config_properties: config properties (could be ConfigObj or a dictionary)
        :type config_properties: Union[configobj.ConfigObj, dict]
        :return: List of connection nodes to aggregate
        :rtype: List[Dict[str, str]]
        """

        return self.inspect_nodes(config_properties)

    def __create_connections(self):
        """
        Create the client if not created yet.
        This method ensures that no more than one single
        time initializing the client (singleton pattern).

        :return: The database connection to work with by client side
        (A new SQLAlchemy session in terms of implementation)
        :rtype: SQLAlchemy session
        """

        self.read_nodes(
            config_properties=main_resources.config[self.MYSQL_SECTION]
        )

    @classmethod
    def get_client(cls, pattern: str = None) -> List[DatabaseClient]:
        """
        Static method for getting database client from pool.

        Retrieve one specific available client from the
        pool instantiated. It does mark that client as used status.

        Allowing here the node searches (when having different
        node connections, giving the specific reference).

        :param pattern: Pattern introduced (could be name or whatever)
        :type pattern: str

        :return: A SQLAlchemy session object
        """

        client_pool: ClientPool = cls.client_pool

        try:
            return client_pool.get_node_client(pattern)
        except exceptions.NodeNotFoundException:
            client_pool.__create_connections()

        return client_pool.get_node_client(pattern)

    @classmethod
    def close(cls, pattern: str):
        try:
            databases_client = cls.get_client(pattern=pattern)
            [
                database_client.client.remove()
                for database_client in databases_client
            ]
        except exceptions.NodeNotFoundException:
            pass
