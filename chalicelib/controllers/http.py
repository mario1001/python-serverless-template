# Created in November 13, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template HTTP module.

Contains an enumeration class with available HTTP request types. Also defines
HTTP response class with serialization for handler layer.
"""

import json
from enum import Enum
from http import HTTPStatus
from typing import Any

import chalicelib.controllers as controllers
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


class HTTPResponse(object):
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

        if not isinstance(value, str):
            value = str(value)

        self.__headers = {
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Origin": value,
            "Access-Control-Allow-Methods": "OPTIONS,POST,GET",
        }

    def __init__(
        self,
        http_status: HTTPStatus = HTTPStatus.OK,
        body: object = None,
        cors_header_url: str = None,
    ):
        """
        Creates an HTTP Response with HTTP status and some body provided.

        Body parameter could be from custom Python DTO (using pydantic per example) or class,
        some specific structure (dictionary or list), whatever you want for body to be used
        in this HTTP response.

        :param http_status: HTTP Status instance (from http module), defaults to HTTPStatus.OK
        :type http_status: HTTPStatus, optional
        :param body: Some specific object to send, defaults to None
        :type body: object, optional
        :param cors_header_url: HTTP Cors default header url, defaults to * (every domain possible)
        :type cors_header_url: str, optional
        """

        if not isinstance(http_status, HTTPStatus):
            http_status = HTTPStatus.OK

        if not cors_header_url:
            cors_header_url = "*"

        self.status_code = http_status.value
        self.headers = cors_header_url
        self.body = body

    def serialize_value(self, body: object):
        if isinstance(body, dict):
            return self.dumps(self.serialize_items(body))

        if isinstance(body, list):
            return self.dumps(self.serialize_items(body))

        if isinstance(body, bytes):
            self.headers["Content-Type"] = "application/octet-stream"
            return body

        # Check if it's a DTO (form dictionary with that)
        data = self.__custom_serialization(body)
        if data is not None:
            return json.dumps(data) if isinstance(data, dict) else data

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
                self.serialize_item(attribute): self.serialize_item(value)
                for attribute, value in items.items()
            }

        if isinstance(items, list):
            return [self.serialize_item(item) for item in items]

        # Worst scenario when having complex objects or simple ones
        # Anyway try the string format standard function

        return str(items)

    @staticmethod
    def dumps(body):
        try:
            return json.dumps(body, ensure_ascii=False)
        except TypeError:
            return body

    def serialize_item(self, item: object):
        if isinstance(item, list) or isinstance(item, dict):

            # Needs serialization inspection for elements
            return self.serialize_items(item)

        if not hasattr(item, "__class__"):
            return item

        data = self.__custom_serialization(item)
        if data is not None:
            return data

        return item

    @staticmethod
    def __custom_serialization(item: object):
        # Class model or DTO instance to serialize
        # Inspect serialization methods and execute them

        pass


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

    @core.register("http")
    def __init__(self) -> None:
        super().__init__()

    def serialize(self, http_status: HTTPStatus, body: Any, headers: Any):
        """
        Main method for serialization process with a HTTP status,
        body and headers as information provided.

        :param http_status: [description]
        :type http_status: HTTPStatus
        :param body: [description]
        :type body: Any
        :param headers: [description]
        :type headers: Any
        """
