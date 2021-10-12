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
from typing import Dict

import chalicelib.core as core
import chalicelib.domain as domain
import chalicelib.controllers as controllers

from aws_resources.exceptions.http_exceptions import BadRequestException

from chalice.app import Request, BadRequestError
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

        return self.parameters.keys()[-1]

    def __init__(self) -> None:
        """
        Creates a parameter controller instance to be used.
        """

        self.parameters = dict()

    def process(
        self,
        request: Request,
        parameters: Dict[str, str],
        pythonic: bool = True,
    ) -> None:
        """
        Main method for processing a AWS Chalice request.

        It saves specific parameters
        and uses a python flag for remaking attributes.

        :param request: original AWS Chalice request
        :type request: Request

        :param parameters: Parameters obtained from specific validation controller
        :type parameters: Dict[str, str]

        :param pythonic: Flag for remaking parameters in pythonic way, defaults to True
        :type pythonic: bool, optional
        """

        parameters_to_save = dict()
        for name, value in parameters.items():

            if pythonic:
                name = self.camel_case_to_snake_case(name)

            parameters_to_save[name] = value

        self.parameters[request] = parameters_to_save

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

        return json.dumps(self.parameters)


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

        :param request: original AWS Chalice request
        :type request: Request

        :param parameters: Extra parameters obtained, defaults to None
        :type parameters: Dict[str, str]

        :param pythonic: Flag for remaking parameters in pythonic way, defaults to True
        :type pythonic: bool, optional
        """

        try:
            body = request.json_body
        except BadRequestError:
            raise BadRequestException(
                error_message="There is an error in body of HTTP request"
            )

        # TODO Should check here for supporting list provided functionality

        # Request body seems to be in the good Python format we want
        return super().process(
            request=request,
            parameters=self.form_data(body),
            pythonic=pythonic,
        )


class PaginationController(QueryParameterController):
    """
    Pagination controller class reference.
    """

    PAGE_ATTRIBUTE = "page"
    PAGE_SIZE_ATTRIBUTE = "page_size"
    ORDER_BY_ATTRIBUTE = "order_by"
    ORDER_TYPE_ATTRIBUTE = "order_type"

    @property
    def pagination(self) -> domain.Pagination:
        return self.__pagination

    @pagination.setter
    def pagination(self, value):
        self.__pagination = value

    @property
    def path(self) -> str:
        return self.__path

    @path.setter
    def path(self, value):
        self.__path = value

    @core.register("pagination")
    def __init__(self, request: Request) -> None:
        """
        Creates a pagination controller with specific
        AWS event parameters dictionary.

        :param event: AWS event
        :type event: dict

        :raises BadRequestException: When page parameter is not an integer
        :raises BadRequestException: When page_size parameter is not an integer
        :raises BadRequestException: When specifying page without providing page size
        :raises BadRequestException: When not field attribute specified along with order type
        """

        self.query_parameters_required = dict()
        self.query_parameters_allowed = {
            self.PAGE_ATTRIBUTE: int,
            self.PAGE_SIZE_ATTRIBUTE: int,
            self.ORDER_BY_ATTRIBUTE: str,
            self.ORDER_TYPE_ATTRIBUTE: str,
        }
        parameters = request.query_params

        pagination = domain.Pagination()

        if parameters:
            self.__init_pagination(parameters, pagination)

        self.pagination = pagination
        self.path = request.context["path"]

        super().__init__(request)

    def __init_pagination(self, parameters, pagination):
        """
        Creates a pagination controller with specific
        AWS event parameters dictionary.

        :param event: AWS event
        :type event: dict

        :raises BadRequestException: When page parameter is not an integer
        :raises BadRequestException: When page_size parameter is not an integer
        :raises BadRequestException: When specifying page without providing page size
        :raises BadRequestException: When not field attribute specified along with order type
        """
        self.__init_page(parameters, pagination)
        self.__init_page_size(parameters, pagination)
        self.__check_page_page_size(pagination)
        self.__init_order_by_order_type(parameters, pagination)

    def __init_page(self, parameters, pagination):
        """
        Creates a pagination controller with specific
        AWS event parameters dictionary.

        :param event: AWS event
        :type event: dict

        :raises BadRequestException: When page parameter is not an integer
        """
        pagination.page = parameters.get(self.PAGE_ATTRIBUTE, None)
        if pagination.page:
            try:
                pagination.page = int(pagination.page)
            except ValueError:
                raise BadRequestException(
                    error_message="El parámetro 'page' tiene que ser un valor entero"
                )

    def __init_page_size(self, parameters, pagination):
        """
        Creates a pagination controller with specific
        AWS event parameters dictionary.

        :param event: AWS event
        :type event: dict

        :raises BadRequestException: When page_size parameter is not an integer
        """
        pagination.page_size = parameters.get(self.PAGE_SIZE_ATTRIBUTE, None)
        if pagination.page_size:
            try:
                pagination.page_size = int(pagination.page_size)
            except ValueError:
                raise BadRequestException(
                    error_message="El parámetro 'page_size' tiene que ser un valor entero"
                )

    def __init_order_by_order_type(self, parameters, pagination):
        """
        Creates a pagination controller with specific
        AWS event parameters dictionary.

        :param event: AWS event
        :type event: dict

        :raises BadRequestException: When page parameter is not an integer
        :raises BadRequestException: When not field attribute specified along with order type
        """
        pagination.order_by = parameters.get(self.ORDER_BY_ATTRIBUTE, None)
        pagination.order_type = parameters.get(
            self.ORDER_TYPE_ATTRIBUTE, domain.OrderType.ASCENDING
        )

        if pagination.order_type is None and not pagination.order_by:
            # Should specify the field to order by
            raise BadRequestException(
                error_message="Debes indicar un atributo para ordenar la consulta."
            )

    @staticmethod
    def __check_page_page_size(pagination):
        """
        Creates a pagination controller with specific
        AWS event parameters dictionary.

        :param event: AWS event
        :type event: dict

        :raises BadRequestException: When specifying page without providing page size
        """
        if pagination.page and not pagination.page_size:
            # Does not make sense at all, pages are oriented with a size page
            raise BadRequestException(
                error_message="Debes indicar un tamaño de página junto con la página asociada."
            )

    def get_pagination_response(self, result: list) -> ResponsePagination:
        """
        Return the pagination response type for the HTTP pagination
        request method. Generic DaaS pagination is creating here
        along with data provided as result.

        Not specifying the items type for avoiding check process
        but should be a list of JSON (dictionary) items for this to
        work well.

        :param result: Serialized result with items to return
        :type result: list

        :return: A new pagination instance with results
        :rtype: ResponsePagination
        """

        pagination = self.pagination

        # Ensure someway somehow that results here are in the format wanted.

        # Quitting the results obtained from queries
        # (partial data, asked for the complete ones)

        pagination.results = result

        return ResponsePagination(**pagination.serialize(self.path))
