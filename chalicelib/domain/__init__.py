# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice domain module.
"""

from abc import ABC, abstractmethod

import chalicelib.controllers as controllers


class Domain(ABC):
    """
    Template domain class reference.

    For creating/using domain classes
    to work with in the template along the
    architecture.
    """

    @staticmethod
    def __is_private(value: str) -> bool:
        """
        Private method for checking it is a private attribute
        along with validation defined.

        :param value: String parameter attached to the model
        :type value: str

        :return: True when considered a private one, otherwise False
        :rtype: bool
        """

        if not value.startswith("_" + Domain.__name__) and not value.startswith("_"):
            return False

        return True

    @abstractmethod
    def serialize(self):
        """
        Serialization process for this instance.

        Default way for domain objects is returning the private attributes
        (vars with underscore mode) ignoring the public ones.

        Example: Private attribute => _Domain__test
                 Private attribute => _test
                 Public attribute => test
        """

        return {
            controllers.http.to_camel_case(key): value
            for key, value in vars(self).items()
            if self.__is_private(key)
        }
