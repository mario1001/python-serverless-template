# Created on June 21, 2021 by Mario Benito
#
# Free Software design purposes at any version of this repository.

"""
MySQL Translator module.

Designs a translator interface for working with sentences.

Dealing with SQL or NoSQL sentences can be an issue when having
too many operators, that's why exists this module along with its definition.
"""

import math
from typing import Dict, Tuple

import chalicelib.domain as domain
import chalicelib.exceptions as exceptions
from sqlalchemy import asc, desc, func
from sqlalchemy.orm.query import Query
from sqlalchemy.orm.session import Session


class MySQLTranslator(object):
    """
    MySQL Translator class reference.

    Traduces some specific request data into SQLAlchemy ORM values
    that would be introduced in that ORM functions (with query or update).

    Executing dynamic code with eval is really a risky thing in an application,
    so we just map sentence functions with specific logic there for dealing with
    user requests.

    Also deals with pagination issues along with queries (if pagination specified
    in the request options instance). Flask-SQLAlchemy provides some functions
    about pagination but DaaS framework won't use that extensions.
    """

    mapping_order = {
        domain.OrderType.ASCENDING: asc,
        domain.OrderType.DESCENDING: desc,
    }

    @property
    def sentences(self) -> Dict[domain.RequestOperations, object]:
        return self.__sentences

    @sentences.setter
    def sentences(self, value):
        self.__sentences = value

    def __init__(self):
        self.sentences = dict()

        self.sentences[domain.RequestOperations.EQUALS] = self.equals_operation
        self.sentences[
            domain.RequestOperations.NOT_EQUALS
        ] = self.not_equals_operation
        self.sentences[domain.RequestOperations.LESS] = self.less_operation
        self.sentences[
            domain.RequestOperations.GREATER
        ] = self.greater_operation
        self.sentences[
            domain.RequestOperations.CONTAINS
        ] = self.contains_operation
        self.sentences[
            domain.RequestOperations.BETWEEN
        ] = self.between_operation
        self.sentences[
            domain.MySQLRequestOperations.EQUALS
        ] = self.equals_operation
        self.sentences[
            domain.MySQLRequestOperations.NOT_EQUALS
        ] = self.not_equals_operation
        self.sentences[domain.MySQLRequestOperations.LESS] = self.less_operation
        self.sentences[
            domain.MySQLRequestOperations.GREATER
        ] = self.greater_operation
        self.sentences[
            domain.MySQLRequestOperations.CONTAINS
        ] = self.contains_operation
        self.sentences[
            domain.MySQLRequestOperations.BETWEEN
        ] = self.between_operation
        self.sentences[domain.MySQLRequestOperations.LIKE] = self.like_operation

    def count_table(self, session: Session, entity: type) -> int:
        """
        Return the table number of rows.

        :param connection: Query ORM instance or session
        :type connection: Query | Session

        :param entity: SQLAlchemy entity class
        :type entity: type

        :return: int
        """

        return session.execute(
            session.query(entity).statement.with_only_columns([func.count()])
        ).scalar()

    def translate_operation(self, wrapper_data: Tuple) -> list:
        """
        Translate specific request database operation into sentences to be executed.

        Should contain the logic behind the sentence management and creation.

        :param wrapper_data: Wrapper data encapsulation to be processed
        (in our case it's the request options along with entity type)
        :type wrapper_data: tuple

        :return: List with sentences translated from request filters
        :rtype: List[str]
        """

        request_options, entity, query, session = wrapper_data

        # Set configuration in the query object (prepare statements in the end)
        # That's the main functionality of this MySQL translator

        for key, filter_request in request_options.request_filters.items():
            request_operation: domain.MySQLRequestOperations = (
                filter_request.request_operation
            )
            sentence: str = self.sentences.get(request_operation, None)

            if not sentence:
                continue

            query = sentence(query, entity, key, filter_request.request_value)

        data = self.paginate_items(
            request_options.pagination, query, entity, session
        )

        #  Checking return values field (if provided serialized values gonna be returned)
        return_values = request_options.return_values
        if return_values:
            data = [item.serialize(return_values) for item in data]

        return data

    def paginate_items(
        self,
        pagination: domain.Pagination,
        query: Query,
        entity: type,
        session: Session,
    ) -> list:
        """
        Handle pagination issues with user request options specified.

        :param pagination: Pagination request options obtained from client
        :type pagination: Pagination

        :param query: Query instance obtained from SQLAlchemy ORM session
        :type query: Query

        :param entity: Entity SQLAlchemy class
        :type entity: type

        :param session: SQLAlchemy session
        :type session: Session

        :raises database_exceptions.RequestException: [description]

        :return: List of MySQL objects
        :rtype: list
        """

        if not pagination:
            return query.all()

        pagination.total_size = len(query.all())

        # Apply order filter operations to query instance
        order_type = pagination.order_type
        order_by = pagination.order_by

        if order_type and order_by:
            query = self.order_by_operation(query, entity, order_by, order_type)

        full_entries = False

        page = pagination.page
        records_per_page = pagination.page_size
        if not page or not records_per_page or page == 0:
            # Page or records (or both) not specified
            # Take every items in one simple page

            pagination.page = 1
            page = 1
            full_entries = True

        # Here comes the count SQLAlchemy method
        total_records = self.count_table(session, entity)

        if total_records == 0:
            return list()

        if not full_entries:

            # Checking page is possible to retrieve
            total_pages = math.ceil(total_records / records_per_page)

            if page > total_pages:

                # Throw page not found exception (request exception in DaaS terms)
                raise exceptions.DatabaseException(
                    "[{MODULE}][{FUNCTION}]: ".format(
                        MODULE=__name__, FUNCTION=self.paginate_items.__name__
                    )
                    + " Page {} cannot exist with {} records per page".format(
                        str(page), str(records_per_page)
                    )
                )

            if records_per_page:
                query = query.limit(records_per_page)
            if page:
                query = query.offset((page - 1) * records_per_page)

        data = query.all()
        pagination.results = data

        return data

    @staticmethod
    def equals_operation(
        query: Query, class_: type, key: str, value: object
    ) -> None:
        """
        Apply an equals filter operation to the query.

        :param query: Session query instance
        :type query: Query

        :param class_: Entity class
        :type class_: type

        :param key: filter key (entity column)
        :type key: str

        :param value: Object value to set in the query
        :type value: object
        """

        return query.filter(getattr(class_, key) == value)

    @staticmethod
    def like_operation(
        query: Query, class_: type, key: str, value: object
    ) -> None:
        """
        Apply an equals filter operation to the query.

        :param query: Session query instance
        :type query: Query

        :param class_: Entity class
        :type class_: type

        :param key: filter key (entity column)
        :type key: str

        :param value: Object value to set in the query
        :type value: object
        """

        return query.filter(getattr(class_, key).like(value))

    @staticmethod
    def not_equals_operation(
        query: Query, class_: type, key: str, value: object
    ) -> None:
        """
        Apply a non-equals filter operation to the query.

        :param query: Session query instance
        :type query: Query

        :param class_: Entity class
        :type class_: type

        :param key: filter key (entity column)
        :type key: str

        :param value: Object value to set in the query
        :type value: object
        """

        return query.filter(getattr(class_, key) != value)

    @staticmethod
    def less_operation(
        query: Query, class_: type, key: str, value: object
    ) -> None:
        """
        Apply a less filter operation to the query.

        :param query: Session query instance
        :type query: Query

        :param class_: Entity class
        :type class_: type

        :param key: filter key (entity column)
        :type key: str

        :param value: Object value to set in the query
        :type value: object
        """

        return query.filter(getattr(class_, key) < value)

    @staticmethod
    def greater_operation(
        query: Query, class_: type, key: str, value: object
    ) -> None:
        """
        Apply a greater filter operation to the query.

        :param query: Session query instance
        :type query: Query

        :param class_: Entity class
        :type class_: type

        :param key: filter key (entity column)
        :type key: str

        :param value: Object value to set in the query
        :type value: object
        """

        return query.filter(getattr(class_, key) > value)

    @staticmethod
    def contains_operation(
        query: Query, class_: type, key: str, value: object
    ) -> None:
        """
        Apply a contains filter operation to the query.

        :param query: Session query instance
        :type query: Query

        :param class_: Entity class
        :type class_: type

        :param key: filter key (entity column)
        :type key: str

        :param value: Object value to set in the query
        :type value: object
        """

        return query.filter(getattr(class_, key).in_(value))

    @staticmethod
    def between_operation(
        query: Query, class_: type, key: str, value: object
    ) -> None:
        """
        Apply a between filter operation to the query.

        :param query: Session query instance
        :type query: Query

        :param class_: Entity class
        :type class_: type

        :param key: filter key (entity column)
        :type key: str

        :param value: Object value to set in the query
        :type value: object
        """

        if not isinstance(value, list):
            value = [value]

        return query.filter(getattr(class_, key).between(*value))

    @classmethod
    def order_by_operation(
        cls, query: Query, class_: type, key: str, order_type: domain.OrderType
    ) -> None:
        """
        Order by specific operation applying with query ORM mapper.

        :param query: Session query instance
        :type query: Query

        :param class_: Entity class
        :type class_: type

        :param key: filter key (entity column)
        :type key: str

        :param order_type: Order type instance
        :type order_type: OrderType
        """

        return query.order_by(
            cls.mapping_order[order_type](getattr(class_, key))
        )


mysql_translator = MySQLTranslator()
