# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice service main module.

Defines the different functions on service layer. Also
here stays the interface for services (every service should
inherit from that class to be injected).

A service must contain business logic operatives (which can differ
from projects) but should remain as a service component definition
with its interface (just as Spring does for example).
"""

from abc import ABC
import chalicelib.core as core


class Service(
    ABC, metaclass=core.ApplicationContext.application_context.injection_class
):
    """
    Abstract service interface reference.
    """
