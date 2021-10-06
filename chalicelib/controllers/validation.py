# Created in June 13, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
PES Topics microservice validation module.

Attempts to the software design decorator pattern.
Also providing a decorator controller for this package to be used.
"""
import json
import re

import chalicelib.core as core
import chalicelib.domain as domain
from aws_resources.exceptions.http_exceptions import BadRequestException
import chalice
from chalice.app import Request
from chalicelib.controllers import Controller
from chalicelib.dto.responses import ResponsePagination


class ParameterController(Controller):
    """
    Parameter controller base class reference.

    Handle parameter validation along
    with path and query ones.

    This class really translate not pythonic-way
    schema parameters into real ones. Should be
    used for Python SonarQube best practices.
    """

    # For passing from Camel case to snake case
    pattern = re.compile(r"(?<!^)(?=[A-Z])")

    @property
    def parameters(self) -> dict:
        return self.__parameters

    @parameters.setter
    def parameters(self, value):
        self.__parameters = value

    def __init__(self, parameters: dict) -> None:
        try:
            # Check initialization firstly
            self.parameters
        except AttributeError:
            self.parameters = dict()

        if not isinstance(parameters, dict):
            return

        self.__pass_filters(parameters)

    def __pass_filters(self, parameters: dict):
        for parameter_name, parameter_value in parameters.items():
            parameter_name = self.camel_case_to_snake_case(parameter_name)

            self.parameters[parameter_name] = parameter_value

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
        return json.dumps(self.parameters)


class PathParameterController(ParameterController):
    """
    Path parameter controller class reference.
    """

    # AWS Gateway Event for lambda function (chalice reformat the request)

    PATH_PARAMETERS_ATTRIBUTE = "pathParameters"

    @property
    def path_parameters(self):
        return self.__path_parameters

    @path_parameters.setter
    def path_parameters(self, value):
        self.__path_parameters = value

    @core.register("uri")
    def __init__(self, request: Request) -> None:
        """
        Creates a controller with path parameters.

        :param parameters: Path parameters in dictionary form
        :type parameters: dict
        """

        parameters = request.uri_params

        self.path_parameters = parameters

        super().__init__(parameters)


class QueryParameterController(ParameterController):
    """
    Query parameter controller class reference.

    One can simply create a query parameter controller specifying
    two properties/fields:
    -QUERY_PARAMETERS_ALLOWED: For allowed ones with validation
    -QUERY_PARAMETERS_REQUIRED: For required ones (does not need
    to be in allowed ones if they are defined here).

    One main important thing is that query properties/
    attributes to search with NEEDS to be in snake case notation
    (no camel case allowed as functionality here).
    """

    # AWS Gateway Event for lambda function (chalice reformat the request)

    QUERY_PARAMETERS_ATTRIBUTE = "queryStringParameters"

    @property
    def query_parameters_allowed(self):
        return self.__query_parameters_allowed

    @query_parameters_allowed.setter
    def query_parameters_allowed(self, value):
        self.__query_parameters_allowed = value

    @property
    def query_parameters_required(self):
        return self.__query_parameters_required

    @query_parameters_required.setter
    def query_parameters_required(self, value):
        self.__query_parameters_required = value

    @property
    def query_parameters(self):
        return self.__query_parameters

    @query_parameters.setter
    def query_parameters(self, value):
        self.__query_parameters = value

    @core.register("query")
    def __init__(self, request: Request) -> None:
        """
        Creates a query parameter controller instance with AWS event.

        :param event: AWS Gateway event
        :type event: dict

        :raises BadRequestException: When no query parameter designed for request
        """

        parameters = request.query_params

        ParameterController.__init__(self, parameters)
        self.query_parameters = parameters

        # Also resetting here the required parameters for next operations
        self.query_parameters_required = {}


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
