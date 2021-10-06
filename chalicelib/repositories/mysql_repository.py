# Created in June 28, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless Template microservice MySQL repository module.
"""

import inspect
from typing import List, Set, Tuple, Union

import chalicelib.core as core
import chalicelib.exceptions as exceptions
import chalicelib.logs as logs
from chalice.app import BadRequestError
from chalicelib.domain import FilterRequest, Pagination, RequestOptions
from chalicelib.domain.models import Audit, MySQL
from chalicelib.repositories import Repository
from chalicelib.repositories.mysql_statement import MySQLStatement
from chalicelib.repositories.mysql_translator import mysql_translator
from sqlalchemy import exc
from sqlalchemy.inspection import inspect as sql_inspect
from sqlalchemy.orm import Query, Session


class BaseRepository(Repository):
    """
    Base MySQL repository class reference.

    Attempts to a base class for basic CRUD implementations
    exposed by repository interface.

    Every new repository should inherit from this class
    for basic implementations (or provide the custom ones).

    Some of the read methods offers sessions as responses providing
    external management, others have a boolean flag for entity relationships
    with internal lazy joins dynamically (activating the flag does not close
    sessions, this should be treated wisely).
    """

    WRITE_NODE = "NODE-RW"
    DOUBLE_UNDERSCORES = "__"

    DEFAULT_DOMAIN_PACKAGE = "chalicelib.domain.models"
    DEFAULT_CLASS_PROPERTY = "__tablename__"

    DELETE_VALID_VALUE = None
    LOGICAL_DELETE_ATTRIBUTE = "deleted_at"

    MYSQL_OPERATIONS = ["SELECT", "INSERT", "UPDATE", "DELETE"]
    COMMIT_CHANGES = {
        "INSERT": True,
        "UPDATE": True,
        "SELECT": False,
        "DELETE": True,
    }

    @property
    def client_pool(self) -> core.ClientPool:
        return self.__client_pool

    @client_pool.setter
    def client_pool(self, value):
        self.__client_pool = value

    @core.register("singleton")
    def __init__(self) -> None:
        self.client_pool = core.ClientPool.client_pool

    @staticmethod
    def rollback(session: Session) -> None:
        """
        Makes a rollback operation within session provided.

        :param session: transaction to apply the rollback
        :type session: Session
        """

        session.rollback()

    @staticmethod
    def flush(session: Session) -> None:
        """
        Makes a flush operation within instance transaction.

        :param session: transaction to apply the flush
        :type session: Session
        """

        session.flush()

    def shutdown(self) -> None:
        """
        Close the entire database control application (all pending transactions
        and SQLAlchemy sessions included in the maker).

        Should only be used when FINISHED every query/insert operation
        with the database client assigned in the whole application.

        It's designed to close every pending feature along the connection in the end.
        """

        for client in self.client_pool.clients:
            client.client.close_all()

    def __commit_operation(
        self, session: Session, make_operations, entities=None
    ):
        """
        Main method for committing an operation (always making the commit)
        after the execution of the method passed as argument (called make_operations).

        Always setting up a timer for the sessions (if timer with seconds provided).
        SQLAlchemy sessions would close always (with timer or directly in finally sentence).

        :param session: SQLAlchemy Session
        :type session: Session

        :param make_operations: method invocation (static function)
        :type make_operations: function | method

        :raises exceptions.DatabaseException: When SQLAlchemy error occurred
        :return: The result of the database operation (should be a list with entities)
        :rtype: list
        """

        if entities is None:
            entities = []
        try:
            result = make_operations(session, entities)

            # commit.  The pending changes above
            # are flushed via flush(), the Transaction
            # is committed, the Connection object closed
            # and discarded, the underlying DBAPI connection
            # returned to the connection pool.

            session.commit()
        except exc.SQLAlchemyError as e:
            # on rollback, the same closure of state
            # as that of commit proceeds.

            logs.system_logger.log(
                "error",
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__commit_operation.__name__
                )
                + "SQLAlchemyError found: {}".format(str(e)),
            )

            session.rollback()
            raise exceptions.DatabaseException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__commit_operation.__name__
                )
                + "SQLAlchemyError found: {}".format(str(e))
            )
        finally:

            # Always closing sessions (managed internally)
            self.close(session)

        return result

    @staticmethod
    def close(session: Session):
        session.close()

    @staticmethod
    def insert_operation(
        session: Session,
        entities: list,
    ):

        session.add_all(entities)

        return entities

    def get_session(self, node_id: str) -> Session:
        """
        Provide SQLAlchemy sessions to manage externally
        out of this base repository. You should be carefully
        using these connections by making the right operations.

        Basically this base repository have a session timer to close
        all sessions created between this layer, but with these ones
        it does not have any control at all.

        :param node_id: Node ID
        :type node_id: str

        :return: Session to use for client
        :rtype: :class: `sqlalchemy.orm.Session`
        """

        return self.__check_connections(node_id)

    def __check_connections(self, pattern):

        clients = self.client_pool.get_client(pattern=pattern)

        if not clients:
            raise exceptions.DatabaseException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__check_connections.__name__
                )
                + "There are no clients configured in the application"
            )

        session: Session = clients.pop().client()
        return session

    def __verify_clients(self, node_id, pattern) -> Session:
        """
        Private method for verifying the database clients
        by checking firstly the nodes and then the rest of possibilities.

        :param node_id: The node to search for (firstly)
        :type node_id: str

        :param pattern: The pattern to search after the node
        :type pattern: str | list

        :raises exceptions.DatabaseException: When no database option is located
        """

        try:
            databases = self.client_pool.get_client(pattern=node_id)
        except exceptions.NodeNotFoundException:
            databases = None

        if not databases:
            session = self.__check_connections(pattern=pattern)

            if session:
                return session

        if not databases:
            raise exceptions.DatabaseException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.find_by_id.__name__
                )
                + "There's no client preconfigured in the environment"
            )

        return databases.pop().client()

    @classmethod
    def query_operations(
        cls,
        session: Session,
        class_: type,
        request_options: RequestOptions,
    ):
        """
        Static method for query operations (different operators, checkout
        request options module for more information).

        :param session: SQLAlchemy session
        :type session: Session

        :param class_: Entity class (ORM model class)
        :type class_: type

        :param request_options: Request options to specify the user query properties
        :type request_options: domain.RequestOptions

        :return: List of entities filtered by query
        :rtype: List[MySQL]
        """

        query: Query = session.query(class_)

        # Translation would prepare query statement before calling it
        data = mysql_translator.translate_operation(
            (request_options, class_, query, session)
        )

        if not data:
            raise BadRequestError(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=cls.query_operations.__name__
                )
                + "There's no data in the query request"
            )

        session.close()
        return data

    def find_entities(
        self, table_name: str, node_id: str = None, relationships: bool = False
    ) -> Union[Tuple[List[MySQL], Session], List[MySQL]]:
        """
        Main method for reading from one database table.

        Reading ORM models without any filter provided
        (you can see that no request options attached
        in the argument specification).

        :param table_name: Database table name (not entity base table)
        :type table_name: str

        :param node_id: Node ID connection to use
        :type node_id: str

        :param relationships: Boolean flag for relationships
        (dynamic lazy joins)
        :type relationships: bool

        :return: List of DaaS domain MySQL objects
        :rtype: Tuple[List[MySQL], Session]
        """

        try:
            session = self.__verify_clients(node_id, self.MYSQL_OPERATIONS[0])
            entity = self.get_entity(table_name=table_name)

            default_request_options = self.__get_default_request_options()
            data: List[Audit] = self.query_operations(
                session, entity, request_options=default_request_options
            )

            if not relationships:
                self.close(session)
                return data

            return data, session
        except BadRequestError:
            self.close(session)
            return []

    def __get_default_request_options(self):
        return RequestOptions(
            request_filters={
                self.LOGICAL_DELETE_ATTRIBUTE: FilterRequest(
                    request_value=self.DELETE_VALID_VALUE
                )
            }
        )

    def find_by_id(
        self,
        entity_id: object,
        table_name: str,
        node_id: str = None,
        relationships: bool = False,
    ) -> Union[Tuple[MySQL, Session], List[MySQL], None]:
        """
        Abstract method for getting an entity by
        its primary key.

        :param entity_id: entity ID to search for
        :type entity_id: object

        :param table_name: Database table name (not entity base table)
        :type table_name: str

        :param node_id: Node ID connection to use
        :type node_id: str

        :param relationships: Boolean flag for relationships
        (dynamic lazy joins)
        :type relationships: bool

        :return: The entity found in database
        :rtype: Tuple[MySQL, Session]
        """

        session = self.__verify_clients(node_id, self.MYSQL_OPERATIONS[0])

        entity = self.get_entity(table_name=table_name)
        query: Query = session.query(entity)

        # Search with primary key method
        data: Audit = query.get(entity_id)

        # Check if data is deleted
        if not data or data.is_logically_deleted():
            self.close(session)
            return None

        if not relationships:
            self.close(session)
            return data

        return data, session

    def find_pagination_entities(
        self,
        table_name: str,
        request_options: RequestOptions,
        node_id: str = None,
    ) -> List[MySQL]:
        """
        Main operation for requesting some type of data.

        Maybe in a future release, DaaS could support several reads
        from different tables, for now it's only one table per method request.

        :param request_options: request options introduced to read from
        :type request_options: RequestOptions

        :param table_name: Table to extract data, defaults to None
        :type table_name: str, optional

        :return: List of domain model objects
        :rtype: List[MySQL]
        """

        database_client = self.client_pool.get_client(
            pattern="SELECT" if not node_id else node_id
        ).pop()
        session: Session = database_client.client()

        if not request_options or not isinstance(
            request_options, RequestOptions
        ):
            raise exceptions.InputParameterException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__,
                    FUNCTION=self.find_pagination_entities.__name__,
                )
                + "a valid RequestOptions instance type (check request_options module)"
            )

        elif not request_options.pagination or not isinstance(
            request_options.pagination, Pagination
        ):
            raise exceptions.InputParameterException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__,
                    FUNCTION=self.find_pagination_entities.__name__,
                )
                + "missing Pagination parameter in RequestOptions"
            )

        data = self.query_operations(
            session, self.get_entity(table_name), request_options
        )
        return data

    def __insert_transaction(self, session, entities):
        return self.__commit_operation(
            session=session,
            make_operations=self.insert_operation,
            entities=entities,
        )

    def create_entity(
        self,
        entity: MySQL,
    ) -> MySQL:
        """
        Abstract method for creating a new entity.

        It's intended to be only for creation firstly,
        but could be implemented with a modification request
        (letting insert/updates in the end).

        :return: The entity created/updated
        :rtype: MySQL
        """

        if isinstance(entity, list) and len(entity) == 1:
            entity = entity[0]
        elif isinstance(entity, list) and len(entity) > 1:
            raise exceptions.InputParameterException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.create_entity.__name__
                )
                + "Can only create one entity with this method!"
            )

        database_client = self.client_pool.get_client(pattern="INSERT").pop()
        session: Session = database_client.client()

        entities = self.__insert_transaction(session, [entity])

        return entities[0]

    @classmethod
    def __validate_entities(cls, entities: List[MySQL]):
        for entity in entities:
            if not isinstance(entity, MySQL):
                raise exceptions.InputParameterException(
                    "[{MODULE}][{FUNCTION}]: ".format(
                        MODULE=__name__,
                        FUNCTION=cls.__validate_entities.__name__,
                    )
                    + "{} is not a MySQL domain model type".format(entity)
                )

    def create_entities(self, entities: List[MySQL]) -> List[MySQL]:
        """
        Implementation method for creating a bunch of entities.

        :param entities: List of entities to save
        :type entities: List[MySQL]

        :return: List of saved entities (with autovalues generated)
        :rtype: List[MySQL]
        """

        self.__validate_entities(entities)

        database_client = self.client_pool.get_client(
            pattern=self.WRITE_NODE
        ).pop()
        session: Session = database_client.client()

        entities = self.__insert_transaction(session, entities)

        return entities

    def update_entity(
        self,
        entity: MySQL,
    ) -> MySQL:
        """
        Abstract method for entity updates.

        Not allowing new creations here,
        it's only reserved for update ones.

        :return: The entity updated
        :rtype: MySQL
        """

        database_client = self.client_pool.get_client(pattern="UPDATE").pop()
        session: Session = database_client.client()

        entities = self.__insert_transaction(session, [entity])
        # Entity is logically deleted
        if entities[0].is_logically_deleted():
            return None

        return entities[0]

    def update_entities(self, entities: List[MySQL]) -> List[MySQL]:
        """
        Abstract method for update a bunch of entities.

        It's intended to be only for update only,
        without the complex way for checking every type.

        This depends on the implementation for each database selected.

        :return: The entity created/updated
        :rtype: MySQL
        """

        self.__validate_entities(entities)

        database_client = self.client_pool.get_client(pattern="UPDATE").pop()
        session: Session = database_client.client()

        entities = self.__insert_transaction(session, entities)

        return entities

    def logical_delete_entity_by_id(
        self,
        entity_id: object,
        table_name: str,
    ):
        """
        Method for entity deletes logically.

        """

        database_client = self.client_pool.get_client(
            pattern=self.WRITE_NODE
        ).pop()
        session: Session = database_client.client()

        entity = self.get_entity(table_name=table_name)
        query: Query = session.query(entity)

        # Search with primary key method
        data: Audit = query.get(entity_id)

        # Data not found phisically
        if not data:
            raise exceptions.BadRequestException(
                error_message=f"Color with id {entity_id} not found"
            )
        # Data not found logically
        elif data.is_logically_deleted():
            raise exceptions.BadRequestException(
                error_message=f"Color with ID {entity_id} not found"
            )

        # Update deleted at entity via delete
        data.delete()

        _ = self.__insert_transaction(session, [data])

    @staticmethod
    def __merge_entities(
        session: Session, entities: List[MySQL]
    ) -> List[MySQL]:
        merge_entities_list = list()

        for entity in entities:

            # Unify by merging the unique entity
            try:
                merge_entities_list.append(session.merge(entity))
            except Exception:
                merge_entities_list.append(entity)

        return merge_entities_list

    def bulk_entities(
        self, entities: List[MySQL], merge_entities: bool = False
    ) -> List[MySQL]:
        """
        Bulk method for saving entities (there's a merge flag for checking
        domain model resources before bulk process).

        Be careful about bulk insertion, does not provide a
        default data flag (flushed values) cause performance could be
        deteriored/affected.

        This method is not supposed for generated values.

        :return: The entity updated
        :rtype: MySQL
        """

        database_client = self.client_pool.get_client(
            pattern=self.WRITE_NODE
        ).pop()
        session: Session = database_client.client()

        if merge_entities:
            entities = self.__merge_entities(session, entities)

        if entities:
            session.bulk_save_objects(entities)

        session.close()
        return entities

    @staticmethod
    def run_native_sql(
        session: Session,
        sql_statements: List[MySQLStatement],
        commit_operation: bool = False,
    ):
        for sql_statement in sql_statements:
            sql_statement.result = session.execute(
                sql_statement.sql_source, sql_statement.mapped_values
            )

        if commit_operation:
            session.commit()

        session.close()
        return None

    @staticmethod
    def get_primary_key(entity) -> List[str]:
        return [key.name for key in sql_inspect(entity.__class__).primary_key]

    @staticmethod
    def get_relationship_keys(entity) -> Set[str]:
        return set(
            {rel.key for rel in sql_inspect(entity.__class__).relationships}
        )

    # When having more models import methods should
    # be in some type of inspect module (to keep in mind)

    @staticmethod
    def import_package(name):
        """
        Loads dynamically some specific package/subpackage.

        :param name: specific path for package
        :type name: str

        :return: object (could be module or class in our case)
        """

        components = name.split(".")
        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod

    @classmethod
    def inspect_domain_model(
        cls, table_name: str, domain_package: str, class_property: str
    ) -> Union[type, None]:
        """
        Main method for getting domain model classes (or other types if so)
        that make references to the table name introduced as parameter.

        Uses inspecting features in some configured module (configured in)
        Returns none value when searches don't provide any located class.

        :param table_name: Table name in domain package
        :type table_name: str
        :return: Custom class instance (with inheritance or not)
        :rtype: type
        """

        domain_package_module = cls.import_package(domain_package)

        for module in dir(domain_package_module):
            if not module.startswith(cls.DOUBLE_UNDERSCORES):
                class_ = getattr(domain_package_module, module)

                if (
                    inspect.isclass(class_)
                    and hasattr(class_, class_property)
                    and getattr(class_, class_property) == table_name
                ):
                    return class_

        # Should be managed externally
        return None

    @classmethod
    def get_entity(cls, table_name):
        entity: Audit = cls.inspect_domain_model(
            table_name=table_name,
            domain_package=cls.DEFAULT_DOMAIN_PACKAGE,
            class_property=cls.DEFAULT_CLASS_PROPERTY,
        )

        if not entity:
            raise exceptions.InputParameterException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=cls.get_entity.__name__
                )
                + "no class mapped to that table introduced"
            )

        return entity

    def count_tables(self, tables: List[str]) -> List[int]:
        """
        Count tables operation.

        :param tables: [description]
        :type tables: List[str]
        :return: [description]
        :rtype: List[int]
        """

        entities = [
            data if isinstance(data, MySQL) else self.get_entity(data)
            for data in tables
            if isinstance(data, str) or isinstance(data, MySQL)
        ]

        database_client = self.client_pool.get_client(
            pattern=self.WRITE_NODE
        ).pop()
        session: Session = database_client.client()

        count_list = list()

        # Translation knows that table functionality
        for entity in entities:
            count_list.append(mysql_translator.count_table(session, entity))

        session.close()
        return count_list

    def execute_sql_statement(
        self, sql_statements: Union[MySQLStatement, List[MySQLStatement]]
    ) -> None:
        """
        Main function for execute native/raw SQL sentences along
        with different parameters. Results are on the SQL statements provided
        in this request.

        DaaS cannot improve certain peaks of performance along with SQL sentences
        with the ORM mapper provided in this framework, that's why supports custom
        SQL statement execution. Some of the expressions would be formed with user
        syntax and DaaS could only offer this execution method for that direct accesses.

        And of course, transaction would be handled by MySQL factory,
        user does not need to concern about that at any way
        (using native way or not along sessions).

        Admits subqueries along with every MySQL syntax sentence to be executed
        along with mapped values. Values should be quoted using the colon signature.
        (presigned with : character format)

        When specifying and using queries here, would attach dynamic SQL items with
        properties specified (if no specified, it would attach custom default
        fields as object properties with respectively values). Take care about
        native SQL results and dynamic MySQL items, they are intended for read data only
        (not allowing write permissions here).

        E.g.::

            mysql_statement = MySQLStatement(
                sql_source='SELECT * FROM my_table WHERE my_column = :val',
                mapped_values={'val': 5},
                properties=('id', 'field', etc...)
            )
            mysql_client.execute_sql_statement(mysql_statement)

            mysql_client.execute_sql_statement(
                [
                    # Different SQL Statements (UPDATE, INSERTS, DELETE OR SELECT)
                    # BE CAREFUL ABOUT MIXIN INSERTS WITH SELECTS (sessions would be closed)
                ]
            )

        :param sql_statements: List of SQL statements
        :type sql_statements: List[MySQLStatement]
        """

        database_operations = list()

        commit_operation = False
        for operation in self.MYSQL_OPERATIONS:
            for sql_statement in sql_statements:
                if (
                    sql_statement.sql_source
                    and operation in sql_statement.sql_source
                ):
                    database_operations.append(operation)

                    if not commit_operation and self.COMMIT_CHANGES.get(
                        operation, False
                    ):
                        commit_operation = True
                    break

        database_client = self.client_pool.get_client(
            pattern=self.MYSQL_OPERATIONS
        ).pop()
        session: Session = database_client.client()

        self.run_native_sql(
            session,
            sql_statements,
            commit_operation,
        )
        session.close()
