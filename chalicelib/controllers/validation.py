# Created in June 13, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless microservice template validation module.

Attempts to the software design decorator pattern.
Also providing a decorator controller for this package to be used.
"""

import json
import re
from typing import Any, Dict, List, Union

import chalicelib.core as core
import chalicelib.domain as domain
import chalicelib.controllers as controllers

import chalicelib.exceptions as exceptions

from chalice.app import MultiDict, Request, BadRequestError
from chalicelib.dto.responses import ResponsePagination


class ParameterController(controllers.ProcessingController):
    """
    Parameter controller base class reference.

    Handle parameter validation along
    with path (called 'uri' as for chalice) and query ones.

    Mantain the serverless definition (only handle one
    request per component construction). But this does not
    mean that using different containers always.

    This class really translate not pythonic-way
    schema parameters into real ones. Should be
    used for Python SonarQube best practices also.
    """

    # For passing from Camel case to snake case
    pattern = re.compile(r"(?<!^)(?=[A-Z])")

    @property
    def requests(self) -> Dict[Request, Dict[str, str]]:
        return self.__requests

    @requests.setter
    def requests(self, value):
        self.__requests = value

    @property
    def last_request(self) -> Request:
        """
        Property for getting the last request inside this controller.

        :return: Last AWS Chalice request obtained from track
        :rtype: chalice.app.Request
        """

        return self.requests.keys()[-1]

    def __init__(self) -> None:
        """
        Creates a parameter controller instance to be used.
        """

        super().__init__()
        self.requests = dict()

    def process(
        self,
        request: Request,
        parameters: Union[Dict[str, Any], List[Any]],
        pythonic: bool = True,
    ) -> None:
        """
        Main method for processing a AWS Chalice request.

        It saves specific parameters
        and uses a python flag for remaking attributes.

        :param request: original AWS Chalice request
        :type request: Request

        :param parameters: Parameters obtained from specific validation controller
        :type parameters: Union[Dict[str, Any], List[Any]]

        :param pythonic: Flag for remaking parameters in pythonic way, defaults to True
        :type pythonic: bool, optional
        """

        if isinstance(parameters, list):
            # Having a list with easy types or not (could be dictionary or internal lists)

            self.requests[request] = parameters
            return

        # Standard case: A simple or complex dictionary
        # (could always contain lists or even other dictionaries)

        parameters_to_save = dict()
        for name, value in parameters.items():

            if (
                isinstance(parameters, MultiDict)
                and "".join(parameters.getlist(name)) != value
            ):
                # Sometimes we need to retrieve the full value in case of strings
                # Just check the overall value and if not the same, just update the var

                value = "".join(parameters.getlist(name))

            if pythonic:
                name = self.camel_case_to_snake_case(name)

            parameters_to_save[name] = value

        self.requests[request] = parameters_to_save

    @classmethod
    def camel_case_to_snake_case(cls, parameter):
        """
        Small function for converting a parameter in format camel
        case into snake case (python standards).

        :param parameter: Parameter name to convert
        :type parameter: str

        :return: Parameter name in snake case
        :rtype: str
        """

        return cls.pattern.sub("_", parameter).lower()

    @staticmethod
    def form_data(parameters: Dict[str, str]) -> Dict:
        if parameters is None:
            parameters = dict()

        return parameters

    def __str__(self):
        """
        Method for string conversion for this object.

        :return: The JSON representation with parameters in string format
        :rtype: str
        """

        return json.dumps(self.requests)


class PathParameterController(ParameterController):
    """
    Path parameter controller class reference.

    Inherits from parameter controller, so it will
    provide the parameters property for saving the ones available to use.
    """

    @core.register("uri")
    def __init__(self) -> None:
        """
        Creates a controller with AWS Chalice request.

        Not really needs any validation, cause path parameters
        are going to be configured within AWS API Gateway and they
        are always required ones.

        :param request: AWS Chalice request obtained from framework
        :type request: chalice.app.Request
        """

        super().__init__()

    def process(
        self, request: Request, parameters=None, pythonic: bool = True
    ) -> None:
        """
        Main method for processing the AWS Chalice request.

        :param request: original AWS Chalice request
        :type request: Request

        :param parameters: URI/Path extra parameters obtained, defaults to None
        :type parameters: Dict[str, str]

        :param pythonic: Flag for remaking parameters in pythonic way, defaults to True
        :type pythonic: bool, optional
        """

        return super().process(
            request=request,
            parameters=self.form_data(request.uri_params),
            pythonic=pythonic,
        )


class QueryParameterController(ParameterController):
    """
    Query parameter controller class reference.

    Component for query validation and mainly getting
    query parameters.
    """

    @core.register("query")
    def __init__(self) -> None:
        """
        Creates a query parameter controller instance to be used.
        """

        super().__init__()

    def process(
        self, request: Request, parameters=None, pythonic: bool = True
    ) -> None:
        """
        Main method for processing the AWS Chalice request.

        :param request: original AWS Chalice request
        :type request: Request

        :param parameters: Query extra parameters obtained, defaults to None
        :type parameters: Dict[str, str]

        :param pythonic: Flag for remaking parameters in pythonic way, defaults to True
        :type pythonic: bool, optional
        """

        return super().process(
            request=request,
            parameters=self.form_data(request.query_params),
            pythonic=pythonic,
        )


class BodyController(ParameterController):
    """
    Body controller base class reference.
    """

    @core.register("body")
    def __init__(self) -> None:
        """
        Creates a body controller instance to be used.
        """

        super().__init__()

    def process(
        self, request: Request, parameters=None, pythonic: bool = True
    ) -> None:
        """
        Main method for processing the AWS Chalice request.

        When having other type on body request (no JSON or list), passing
        that value on a list as a request for the parameter controller.

        :param request: original AWS Chalice request
        :type request: Request

        :param parameters: Extra parameters obtained, defaults to None
        :type parameters: Dict[str, str]

        :param pythonic: Flag for remaking parameters in pythonic way, defaults to True
        :type pythonic: bool, optional
        """

        try:

            # JSON cases would be fine with this
            body = request.json_body
        except BadRequestError:

            # Body is not in JSON format
            # Just save it in a list for super calls

            return super().process(
                request=request,
                parameters=[request._body],
                pythonic=pythonic,
            )

        # Request body seems to be in the good Python format we want
        return super().process(
            request=request,
            parameters=self.form_data(body),
            pythonic=pythonic,
        )
