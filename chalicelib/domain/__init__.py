# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice domain module.
"""

from abc import ABC, abstractmethod


class Domain(ABC):
    """
    Template domain class reference.

    For creating/using domain classes
    to work with in the template along the
    architecture.
    """

    @abstractmethod
    def serialize(self):
        raise NotImplementedError(
            "You should specify an implementation"
            "for serialization process"
        )
