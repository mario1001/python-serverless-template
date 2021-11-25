# Created in November 13, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template HTTP module.

Contains an enumeration class with available HTTP request types. Also defines
HTTP response class with serialization for handler layer.
"""

from __future__ import annotations

import json
from enum import Enum
from http import HTTPStatus
from typing import Any, Dict, Iterable, Union

from pydantic import BaseModel

import chalicelib.core.serialization as serialization
import chalicelib.controllers as controllers
import chalicelib.domain as domain
import chalicelib.core as core


def to_camel_case(snake_str) -> str:
    """
    Little function for passing from snake case vars
    into camel ones.

    :param snake_str: Variable in snake case in string format
    :type snake_str: str

    :return: camel case var name
    :rtype: str
    """

    components = snake_str.split("_")
    # We capitalize the first letter of each component except the first one
    # with the 'title' method and join them together.
    return components[0] + "".join(x.title() for x in components[1:])


class HTTPResponse(domain.Domain):
    """
    HTTP Response class reference.

    Contains the status code and body properties.

    Also provides a method for serialize responses
    into JSON format (dictionary as Python type).

    AWS Services could envelop here its custom data into
    the body property (would be making conversions needed
    for API Gateway returned response).
    """

    @property
    def http_controller(self) -> HTTPController:
        return self.http_controller

    @http_controller.setter
    def http_controller(self, value):
        self.http_controller = value

    @property
    def status_code(self):
        return self.__status_code

    @status_code.setter
    def status_code(self, value):
        self.__status_code = value

    @property
    def body(self):
        return self.__body

    @body.setter
    def body(self, value):

        # Check objects serialization (if so)
        self.__body = self.serialize_value(value)

    @property
    def headers(self):
        return self.__headers

    @headers.setter
    def headers(self, value):
        if isinstance(value, Iterable):
            value = ",".join(
                [str(data) if not isinstance(data, str) else data for data in value]
            )

        if not isinstance(value, str):
            value = str(value)

        self.__headers = {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": value,
            "Access-Control-Allow-Methods": "*",
        }

    def __init__(
        self,
        controller: HTTPController,
        http_status: HTTPStatus = HTTPStatus.OK,
        body: object = None,
        cors_url: Union[str, Iterable] = None,
    ):
        """
        Creates an HTTP Response with HTTP status and some body provided.

        Body parameter could be from custom Python DTO (using pydantic per example) or class,
        some specific structure (dictionary or list), whatever you want for body to be used
        in this HTTP response.

        You can include CORS url domains (or custom classes with string method conversion)
        as an iterable (list, set or tuple for example) or just by specifying
        in string format ('domain_unique', 'domain1, domain2, ...').

        :param http_status: HTTP Status instance (from http module), defaults to HTTPStatus.OK
        :type http_status: HTTPStatus, optional
        :param body: Some specific object to send, defaults to None
        :type body: object, optional
        :param cors_header_url: HTTP Cors default header url, defaults to * (every domain possible)
        :type cors_header_url: str or Iterable, optional
        """

        if not isinstance(http_status, HTTPStatus):
            http_status = HTTPStatus.OK

        if not cors_url:
            cors_url = "*"

        self.status_code = http_status.value
        self.headers = cors_url
        self.body = body
        self.http_controller = controller

    def serialize_value(self, body: object):
        if isinstance(body, dict) or isinstance(body, list):
            # Prepare standard response (with UTF-8-encoded JSON string as text payload)

            return self.dumps(self.serialize_items(body))

        if isinstance(body, bytes):
            # Prepare this response for a binary payload

            self.headers["Content-Type"] = "application/octet-stream"
            return body

        # Use custom serialization module to check it from there
        body = self.http_controller.serialize_item(body, self)
        if body is not None:
            return json.dumps(body)

        # Worst scenario when having complex objects or simple ones
        # Anyway try the string format standard function

        return str(body)

    def serialize_items(self, items: object):
        """
        Recursive function for serialize specific items passed.

        Serialization is just an iterative process with conversions (if needed)
        and preparing items to be dumped (if dictionary or list structure)

        :param items: Items to be serialized
        :type items: object

        :return: Wrapper serialized object
        :rtype: object
        """

        if isinstance(items, dict):
            return {
                self.http_controller.serialize_item(
                    attribute, self
                ): self.http_controller.serialize_item(value, self)
                for attribute, value in items.items()
            }

        if isinstance(items, list):
            return [self.http_controller.serialize_item(item, self) for item in items]

        # Worst scenario when having complex objects or simple ones
        # Anyway try the string format standard function

        return str(items)

    @staticmethod
    def dumps(body):
        try:
            return json.dumps(body, ensure_ascii=False)
        except TypeError:
            return body


class HTTPRequestTypes(Enum):
    """
    HTTP request types enumeration class.

    Defines the available HTTP Request types along
    with RESTful API best practices.
    """

    GET = "get"
    POST = "post"
    PUT = "put"
    DELETE = "delete"
    PATCH = "patch"


class HTTPController(controllers.Controller):
    """
    HTTP Controller class reference.

    Uses core serialization module for managing
    HTTP responses for the handlers.
    """

    SERIALIZERS: Dict[object, serialization.Serializer]

    @core.register("http")
    def __init__(self) -> None:
        super().__init__()

        self.SERIALIZERS = {
            BaseModel: serialization.PydanticSerializer,
            serialization.domain.Domain: serialization.DomainSerializer,
        }

    def request_http_response(
        self, http_status: HTTPStatus, body: Any, cors_url: Union[str, Iterable] = None
    ) -> HTTPResponse:
        """
        Main method for requesting a HTTP response with status, body and headers
        provided as parameters.

        Responses are not shared (or not supposed to be used like that neither caching responses)
        and are returned in time execution for now. Each case depends on the HTTP request and have
        only one way for answering.

        :param http_status: HTTP status instance for code assignment
        :type http_status: HTTPStatus

        :param body: Body to write as response (ensuring string conversion)
        :type body: Any

        :param cors_url: Union[str, Iterable], default to None
        :type cors_url: HTTPStatus

        :return: a new HTTP response created for this case
        :rtype: object
        """

        return HTTPResponse(http_status=http_status, body=body, cors_url=cors_url)

    def serialize_item(self, item: object, http_response: HTTPResponse) -> dict:
        if isinstance(item, list) or isinstance(item, dict):

            # Needs serialization inspection for elements
            # using HTTP response method for that

            return http_response.serialize_items(item)

        # Just check types and associate specific strategy for serialization
        for type, strategy in self.SERIALIZERS.items():
            if isinstance(item, type):
                core.inject(ref=strategy)
                return strategy.instance.to_json(item)

        # Worst scenario: use the default dict converter from object
        # It should be introduced an object (if not this would fail anyway)

        return item.__dict__
