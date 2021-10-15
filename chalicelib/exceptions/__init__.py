# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice main exceptions module.

Defines the exceptions for each layer, depending on the
modules here (organization and hierarchy).
"""

from chalicelib.exceptions.core_exceptions import (
    ClientNotFoundException,
    DependencyInjectionException,
    NodeNotFoundException,
    BeanNotFoundException,
)
from chalicelib.exceptions.handler_exceptions import (
    MAPPED_MESSAGES,
    BadRequestException,
    HTTPRequestException,
    InternalServerErrorException,
    NotImplementedException,
    UnauthorizedException,
    UnavailableServiceException,
)
from chalicelib.exceptions.repository_exceptions import DatabaseException
from chalicelib.exceptions.security_exceptions import AuthenticationException
from chalicelib.exceptions.service_exceptions import ServiceRequestException
from chalicelib.exceptions.validation_exceptions import InputParameterException
