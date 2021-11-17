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
from typing import List, Union

from pydantic import BaseModel

import chalicelib.exceptions as exceptions


class Serializer(ABC):
    """
    Serializer abstract base class reference.

    Defines the operations needed for serialization process.
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

    def to_json(self, value: Union[BaseModel, List[BaseModel]]) -> dict:
        """
        Basic JSON serialization process implementation for a DTO model.

        :param value: Pydantic object (model)
        :type value: BaseModel
        :return: A dictionary representation for the object
        :rtype: dict
        """

        if isinstance(value, list):
            return self.__serialize_items(value)

        if not isinstance(value, BaseModel):
            raise exceptions.SerializationException()

        return value.dict()

    def __serialize_items(self, items: list):
        """
        Serialize a list of items (ensuring a list here).

        Passes along different instances of Pydantic models
        (implementation cannot check types here).

        :param items: [description]
        :type items: list
        """

        return [item.dict() for item in items if isinstance(item, BaseModel)]
