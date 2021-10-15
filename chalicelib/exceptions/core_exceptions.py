# Created in June 15, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template Microservice core exception module.

Defines the core micro-framework exceptions when having
some different situations (this core exceptions could be treated or not).
"""


class NodeNotFoundException(Exception):
    """
    Node not found exception base class.

    For scenarios when a node is not present
    in the data structure.
    """


class ClientNotFoundException(Exception):
    """
    Client not found exception base class.

    For scenarios when database client (or any type
    of client, could be AWS Resource library client per example).
    is not found in the context registry.
    """


class DependencyInjectionException(Exception):
    """
    Dependency Injection (DI) exception class reference.

    Basically raised when trying to inject some component
    not registered in the context application.
    """


class BeanNotFoundException(Exception):
    """
    Bean not found exception class reference.

    Raised when using a bean translator for searching
    application components and process has not successful result.
    """
