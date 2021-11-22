# Created in November 16, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless serialization module in core functionalities.

Components for serialization tools. It's not the definition of
controllers (that would be on the controller layer), just a set
of serializers to be used.
"""

from abc import ABC, abstractmethod

from pydantic import BaseModel

import chalicelib.exceptions as exceptions
import chalicelib.domain as domain


class Serializer(ABC):
    """
    Serializer abstract base class reference.

    Defines the operations needed for serialization process. This process
    could be from passing from JSON to class model or the other way around.

    There is no a certain definition of serialization as itself, so just
    setup the methods here for object conversions.
    """

    @abstractmethod
    def to_json(self, value: object) -> dict:
        """
        JSON serialization process for a value.

        :param value: Specific value to serialize
        :type value: object

        :return: A dictionary representing a JSON format
        :rtype: dict
        """


class PydanticSerializer(Serializer):
    """
    Pydantic serializer class reference.
    """

    def to_json(self, item: BaseModel) -> dict:
        """
        Basic JSON serialization process implementation for a DTO model.

        :param item: Pydantic object (model)
        :type item: BaseModel
        :return: A dictionary representation for the object
        :rtype: dict
        """

        if not isinstance(item, BaseModel):
            raise exceptions.core_exceptions.SerializationException()

        return item.dict()


class DomainSerializer(Serializer):
    """
    Pydantic Custom domain serializer class reference.

    For domain custom objects of this template. There is a
    domain custom class with abstract methods for serialization.
    """

    def to_json(self, item: object) -> dict:
        """
        Basic JSON serialization process implementation
        for a custom domain model.

        :param item: Custom Domain object (model)
        :type item: object
        :return: A dictionary representation for the object
        :rtype: dict
        """

        if not isinstance(item, domain.Domain):
            raise exceptions.core_exceptions.SerializationException()

        return item.serialize()
