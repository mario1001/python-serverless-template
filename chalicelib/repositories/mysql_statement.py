# Created on June 21, 2021 by Mario Benito
#
# Free Software design purposes at any version of this repository.

"""
MySQL Statement module.

Contains the SQL statements that can be introduced in the native
support SQL part of MySQL client operations. Introducing a new way of
executing different sentences along with DaaS framework.
"""

from collections.abc import Iterable
from typing import Dict

from chalicelib.domain.models import MySQL
from sqlalchemy.engine.result import ResultProxy


class MySQLStatement(object):
    """
    MySQL statement class reference.

    Defines an SQL sentence/statement with mapped values
    and properties values for the native query operations.

    Dynamic objects will be mapped in this class along result
    attributes (checkout the attributes firstly before using it).

    It's just an envelop for encapsulating native queries or other
    insert/update sentences to be executed by SQLAlchemy sessions
    managed by factory feature.
    """

    SEQUENCE = "&SEQUENCE&"
    DYNAMIC_SQL_FIELD = "dynamic_property" + SEQUENCE

    def __init__(
        self,
        sql_source: str,
        mapped_values: Dict[str, object] = None,
        properties: Iterable = None,
    ) -> None:
        """
        Creates an SQL statement with provided values.

        One thing you need to know is that introduced properties are going
        to be removed for the last sentence execution, result will be generated
        with that properties (needed on demand).

        :param sql_source: Sentence to execute (should be in string format)
        :type sql_source: str
        :param mapped_values: Dictionary with mapped values for sentence
        :type mapped_values: Dict[str, object]
        :param properties: Structure with fields/properties attached to the dynamic objects
        :type properties: Iterable
        """

        self.sql_source = sql_source
        self.mapped_values = mapped_values

        if not properties:
            properties = list()
        elif isinstance(properties, Iterable):
            properties = list(properties)

        self.properties = properties

    def create_dynamic_objects(self, result_as_list):
        sql_list = list()

        for row in result_as_list:

            # Initialize dynamic SQL items (should be used wisely)
            dynamic_item = MySQL()
            property_index = 0
            sequence = 1

            # This should be a tuple with SQL values
            for value in row:

                # This is the raw value or property to set
                if self.properties and property_index < len(self.properties):
                    attribute = self.properties[property_index]
                    property_index += 1
                else:
                    attribute = self.DYNAMIC_SQL_FIELD.replace(
                        self.SEQUENCE, str(sequence)
                    )
                    sequence += 1

                setattr(dynamic_item, attribute, value)

            sql_list.append(dynamic_item)

        return sql_list

    @property
    def result(self):
        return self.__result

    @result.setter
    def result(self, result):
        # Check if query result is provided here
        # If so, create dynamic MySQL objects with concrete formats

        if isinstance(result, ResultProxy):
            result = self.create_dynamic_objects(result.fetchall())

        self.__result = result
