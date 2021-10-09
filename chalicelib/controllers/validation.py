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
from typing import Any, Dict, List, Tuple

import chalicelib.core as core
import chalicelib.domain as domain
from aws_resources.exceptions.http_exceptions import BadRequestException
import chalice
from chalice.app import Request
from chalicelib.controllers import Controller
from chalicelib.dto.responses import ResponsePagination


class RequestParameter(object):
    """
    Request Parameter class specification for this module.

    Represents a request parameter obtained from AWS Gateway, contains name, type and value
    for validation module.
    """

    @property
    def name(self) -> str:
        return self.__name

    @name.setter
    def name(self, value):
        self.__name = value

    @property
    def type(self) -> object:
        return self.__type

    @type.setter
    def type(self, value):
        self.__type = value

    @property
    def value(self) -> Any:
        return self.__value

    @value.setter
    def value(self, value):
        self.__value = value

    @property
    def required(self) -> bool:
        return self.__required

    @required.setter
    def required(self, value):
        self.__required = value

    def __init__(self, name: str, value: str, required: bool = True) -> None:
        """
        Creates a request parameter instance.

        :param name: The parameter name (key, field as you want)
        :type name: str
        :param type: [description]
        :type type: [type]
        :param value: [description]
        :type value: str
        :param required: Mandatory flag, defaults to True
        :type required: bool, optional
        """

        self.name = name

        self.type = self.accurate_type(value)
        self.value = self.type(value)
        self.required = required

    @staticmethod
    def accurate_type(type: str) -> object:

        # Try the integer conversion
        try:
            return int(type)
        except ValueError:
            pass

        # Try with floating conversion
        try:
            return float(type)
        except ValueError:
            pass

        return type


class StrictRequestParameter(RequestParameter):
    """
    Strict request parameter class.
    """

    @property
    def allowed(self) -> bool:
        return self.__allowed

    @allowed.setter
    def allowed(self, value):
        self.__allowed = value


class ParameterController(Controller):
    """
    Parameter controller base class reference.

    Handle parameter validation along
    with path (called 'uri' as for chalice) and query ones.

    Mantain the serverless definition (only handle one
    request per component construction).

    This class really translate not pythonic-way
    schema parameters into real ones. Should be
    used for Python SonarQube best practices also.
    """

    # For passing from Camel case to snake case
    pattern = re.compile(r"(?<!^)(?=[A-Z])")

    @property
    def parameters(self) -> List[RequestParameter]:
        return self.__parameters

    @parameters.setter
    def parameters(self, value):
        self.__parameters = value

    def __init__(
        self, parameters: Dict[str, Tuple[str, bool]], pythonic: bool = True
    ) -> None:
        """
        Creates a parameter controller with specific parameters (with options inside)
        and a python flag for remaking attributes.

        What we mean with configuration/options is the detail for that parameter (required
        or not, etc...)

        :param parameters: Dictionary with keys as names and values along with configuration
        :type parameters: Dict[str, Tuple[str, bool]]
        :param pythonic: [description], defaults to True
        :type pythonic: bool, optional
        """

        self.parameters = list()
        for name, properties in parameters.items():
            value, required = properties

            if pythonic:
                name = self.camel_case_to_snake_case(name)

            request_parameter = RequestParameter(name, value, required)
            self.parameters.append(request_parameter)

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
    def __init__(self, request: Request, pythonic: bool = True) -> None:
        """
        Creates a controller with AWS Chalice request.

        Not really needs any validation, cause path parameters
        are going to be configured within AWS API Gateway and they
        are always required ones.

        :param request: AWS Chalice request obtained from framework
        :type request: chalice.app.Request
        """

        parameters = request.uri_params

        if parameters is None:
            parameters = dict()

        super().__init__(
            {parameter: (value, True) for parameter, value in parameters},
            pythonic,
        )


class QueryParameterController(ParameterController):
    """
    Query parameter controller class reference.

    Creating a query controller instance needs some specific
    configuration along with the class constructor attributes.

    You can define a query controller for some specific
    AWS Chalice request validation. Design your configuration
    as you want when instance creation.
    """

    @property
    def configuration(self) -> List[RequestParameter]:
        return self.__configuration

    @configuration.setter
    def configuration(self, value):
        self.__configuration = value

    @core.register("query")
    def __init__(
        self,
        request: Request,
        configuration: List[RequestParameter] = None,
        pythonic: bool = True,
    ) -> None:
        """
        Creates a query parameter controller instance with parameters.

        Configuration The list of request parameters would be created right here along with
        parameter validations or verifications.

        :param request: [description]
        :type request: Request
        :param configuration: [description], defaults to None
        :type configuration: List[RequestParameter], optional
        :param pythonic: [description], defaults to True
        :type pythonic: bool, optional
        """

        if configuration is None:
            configuration = list()

        # Set configuration firstly
        self.configuration = configuration
        parameters = request.query_params

        if parameters is None:
            parameters = dict()

        query_parameters_allowed = [
            parameter.name
            for parameter in self.configuration
            if (
                isinstance(parameter, StrictRequestParameter)
                and parameter.allowed
            )
            or isinstance(parameter, RequestParameter)
        ]
        query_parameters_required = [
            parameter.name
            for parameter in self.configuration
            if isinstance(parameter, RequestParameter) and parameter.required
        ]

        # Make validation right here with configuration
        for parameter, value in parameters.items():

            # Check if snake case (or conversion to that)
            if pythonic:
                parameter = self.camel_case_to_snake_case(parameter)

            if parameter not in query_parameters_allowed:
                raise BadRequestException(
                    error_message="Query parameter "
                    "{} is not allowed for this endpoint".format(parameter)
                )

            if parameter in query_parameters_required:
                del query_parameters_required[parameter]

            parameters[parameter] = value

        if query_parameters_required:
            raise BadRequestException(
                error_message="Query required parameters "
                "{} for this endpoint".format(query_parameters_required)
            )

        super().__init__(self, parameters, pythonic)


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


class BodyController(ParameterController):
    """
    Body controller base class reference.
    """

    BODY_ATTRIBUTE = "body"

    @core.register("singleton")
    def __init__(self, request: Request) -> None:
        """
        Creates a body controller instance with AWS event.

        HTTP request type should be granted as a precondition
        for body creation in the service request.

        :param request: AWS Chalice event request
        :type event: :class: `chalice.app.Request`
        """

        try:
            body = request.json_body
        except chalice.app.BadRequestError:
            raise BadRequestException(
                error_message="There is an error in body of HTTP request"
            )

        # Request body seems to be in the good Python format we want
        super().__init__(body)
