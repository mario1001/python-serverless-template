# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template Microservice handler exceptions main module.

Handlers would use these exceptions for answering to the request
API Gateway. Also some of the responses are generated with the exceptions.
"""

from aws_resources.exceptions import (
    BadRequestException,
    HTTPRequestException,
    InternalServerErrorException,
    NotImplementedException,
    UnauthorizedException,
    UnavailableServiceException,
)
from aws_resources.exceptions.http_exceptions import MAPPED_MESSAGES
