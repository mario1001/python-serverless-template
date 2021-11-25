# Created in November 25, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template with Domain Base SQL definition module.
"""

from datetime import datetime
from typing import List, Dict
from sqlalchemy import Column, DateTime, Integer
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_serializer import SerializerMixin


Base = declarative_base()


class MySQL(Base, SerializerMixin):
    """
    MySQL entity base class.

    Provides a serialization custom method (called to_json)
    and some few properties that would be necessary for certain
    subclasses.

    Any dynamical way for object creation should be added here
    in this magical parent class. Be really careful about this,
    DaaS could have control over the dynamic initialization but
    SQLAlchemy sessions do not know anything about them.

    There's only one reason for dynamic creation: SQL native queries
    could have used/mixed this tool for composing classes.
    """

    __abstract__ = True

    ONLY_ATTRIBUTE = "only"

    def deserialize(self, json_object: dict) -> None:
        """
        Deserialize an entity aggregating properties with a dictionary.

        This method is ONLY valid for populating own static attributes defined
        in its domain template, this method does not allow dynamic aggregations
        by itself for subclasses implementations. Dynamic attributes and classes
        are managed internally and can only be modified (for now) for DaaS library layes.

        This method checks if properties exists in the entity and poblate
        them with specific value found in the dictionary object.

        :param json_object: Mapped values in a dictionary to poblate
        :type json_object: dict
        """

        dynamic_attribute = False
        if self.dynamic_type():
            dynamic_attribute = True

        for property, value in json_object.items():
            # Distinguise between direct MySQL class for dynamic attributes or not

            if dynamic_attribute:
                setattr(self, property, value)
                continue

            if hasattr(self, property):
                setattr(self, property, value)

    def dynamic_type(self) -> bool:
        return type(self) == MySQL

    def serialize(self, return_values: List[str] = None) -> Dict[str, object]:
        """
        Returns a JSON representation of this object.

        Custom dynamic MySQL instances (direct type ones) does not use
        SQLAlchemy-serialize module, they are treated differently with a custom
        serialize implementation.

        This could be override with children DynamoDB custom domain.

        :return: The object dictionary serialized
        :rtype: Dict[str, object]
        """

        if self.dynamic_type():
            self_json = self.__dict__

            if not return_values:
                return self_json

            return {
                attribute: value
                for attribute, value in self.__dict__.items()
                if attribute in return_values
            }

        serialize_parameters = dict()

        if return_values:
            serialize_parameters[self.ONLY_ATTRIBUTE] = tuple(return_values)

        return self.to_dict(**serialize_parameters)


class Audit(MySQL):
    """
    Auditory base class reference. Inherits directly from MySQL
    base class cause SQLAlchemy does not support multiple
    inheritance yet.

    Contains the auditory data/information to
    be generated in PES MySQL tables. Also provides
    a method that populate audit fields/properties.

    There is no default user ID (like ADMIN or something
    like that). Each service should provide the user ID
    for creation/update audit data.

    Audit properties provided by this class:
    - Creation/Update date
    - Creation/Update user ID (not Foreign Key)
    """

    __abstract__ = True

    created_by = Column(Integer, default=None)
    updated_by = Column(Integer, default=None)
    created_at = Column(DateTime, default=None)
    updated_at = Column(DateTime, default=None)
    deleted_at = Column(DateTime, default=None)

    def create_audit(self, user_id: int) -> None:
        """
        Audits the specific new entity instance. Ensure
        this entity object is a new one for ORM creation.

        Generates auditory fields automatically which
        fills created/updated date and created/updated names.

        :param user_id: User ID (mandatory)
        :type user_id: int
        """

        self.created_at = datetime.now()
        self.created_by = user_id

    def update_audit(self, user_id: int) -> None:
        """
        Update the auditory fields.

        Fills the modified properties:
        - updated_date (current date)
        - updated_by (user ID provided)

        :param user_id: User ID (mandatory)
        :type user_id: str
        """
        self.updated_at = datetime.now()
        self.updated_by = user_id

    def delete(self) -> None:
        """
        Delete data by adding deleted_at
        """
        self.deleted_at = datetime.now()

    def is_valid(self) -> bool:
        """
        Check if an item has not been deleted logically
        """
        return self.deleted_at is None

    def is_logically_deleted(self) -> bool:
        """
        Check if an item has been deleted logically
        """
        return self.deleted_at is not None
