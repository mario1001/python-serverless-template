# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template Microservice service exception module.

Defines service exceptions to be raised and captured in that layer,
not pretending to catch them in the controller layer (neither the handler layer).

Service layer needs to manage program flow perfectly, that's why we define
these exceptions, a good file handle should be done here.
"""


class ServiceRequestException(Exception):
    """
    Service request class reference for launching
    custom exceptions in service layer.
    """
