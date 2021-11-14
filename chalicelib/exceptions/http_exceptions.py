# Created in November 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template HTTP Exceptions module.

This module provides default HTTP request exceptions with
default (or customized) error messages.

Each HTTP exception have a method for generating a specific
HTTP response (using HTTP controller layer).
"""

from http import HTTPStatus

import chalicelib.controllers as controllers

MAPPED_MESSAGES = {
    HTTPStatus.BAD_REQUEST.value: "El servidor no pudo interpretar la solicitud dada una sintáxis inválida.",
    HTTPStatus.INTERNAL_SERVER_ERROR.value: "El servidor ha encontrado una situación que no sabe como manejarla. Error interno.",
    HTTPStatus.UNAUTHORIZED.value: "El cliente no se ha autenticado correctamente.",
    HTTPStatus.OK.value: "OK",
    HTTPStatus.SERVICE_UNAVAILABLE.value: "El servidor no está listo para manejar la petición. Causas comunes puede ser que el servidor está caído por mantenimiento o está sobrecargado.",
    HTTPStatus.NOT_IMPLEMENTED.value: "El metodo solicitado no está soportado por el servidor y no puede ser manejado",
    HTTPStatus.NOT_FOUND.value: "El servidor no pudo encontrar el contenido solicitado.",
}


class HTTPRequestException(Exception):
    """
    HTTP request exception for AWS services.

    Default exception would be an internal server error
    (500 as HTTP status code and default error message).

    Contains two methods: one for generate a HTTP response associated
    along with the other for serialization.
    """

    HTTP_STATUS: HTTPStatus = HTTPStatus.INTERNAL_SERVER_ERROR
    MESSAGE: str = "The server has encountered a situation that cannot be handled. Internal error."

    def __init__(
        self,
        http_status: HTTPStatus = None,
        message: str = None,
    ):
        """
        Creates an HTTP Request exception with status code and message assigned.

        Really intended for HTTP flows (not only error exceptions per example).

        :param http_status_code: HTTP Status code, defaults to STATUS_CODE attribute
        :type http_status_code: :class: `http.HTTPStatus`, optional
        :param message: Message as body answer, defaults to None
        :type message: str, optional
        """

        if isinstance(http_status, HTTPStatus):
            self.HTTP_STATUS = http_status

        if isinstance(message, str):
            self.MESSAGE = message


class HTTPErrorException(HTTPRequestException):
    """
    HTTP error request exception class reference.

    Contains a method for generating the HTTP
    response to resolve the request.
    """

    def get_response(
        self, cors_header_url: str = None
    ) -> controllers.http.HTTPResponse:
        """
        Generates a new HTTP response accorded to this event.

        Usually CORS header urls are configured in resources
        (maybe this parameter should be gone).

        :param cors_header_url: Header CORS default url, default to * (allow everything)
        :type cors_header_url: str

        :return: A new HTTP response object
        :rtype: :class: `aws_resources.restful_api.http_response.HTTPResponse`
        """

        message_response = controllers.http.HTTPResponse(
            http_status=self.HTTP_STATUS,
            body=self.MESSAGE,
            cors_header_url=cors_header_url,
        )

        # Returning this response with message generated automatically
        # Note message is default when no providing information there

        return message_response


class BadRequestException(HTTPErrorException):
    """
    Bad Request exception class reference.

    Represents a 400 Bad request HTTP Error, this status code
    is raised when founding strange data in the handler
    validation process.
    """

    DEFAULT_HTTP_STATUS: HTTPStatus = HTTPStatus.BAD_REQUEST


class NotImplementedException(HTTPErrorException):
    """
    Not Implemented exception class reference.

    Represents a 501 Not Implemented Service type HTTP Error.
    """

    DEFAULT_HTTP_STATUS: HTTPStatus = HTTPStatus.NOT_IMPLEMENTED


class InternalServerErrorException(HTTPErrorException):
    """
    Internal Server Error exception class reference.

    Represents a 500 Internal Server HTTP Error, this status code
    is raised when founding strange data in the handler
    validation process.
    """


class UnauthorizedException(HTTPErrorException):
    """
    Unauthorized exception class reference.
    """

    DEFAULT_HTTP_STATUS: HTTPStatus = HTTPStatus.UNAUTHORIZED


class UnavailableServiceException(HTTPErrorException):
    """
    Unavailable Service exception class reference.
    """

    DEFAULT_HTTP_STATUS: HTTPStatus = HTTPStatus.SERVICE_UNAVAILABLE
