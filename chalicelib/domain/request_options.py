from enum import Enum, auto
from typing import Dict, List, Union
import math
import urllib.parse

# noinspection PyCompatibility
import chalicelib.exceptions as exceptions
from chalicelib.resources import resources


class RequestOperations(Enum):
    """
    Request operations enumeration class.

    Contains the different operators supported in DaaS service.

    Each operator should be assigned in the specific database package.
    DaaS service first version only supports these few ones.
    """

    EQUALS = auto()
    NOT_EQUALS = auto()
    LESS = auto()
    GREATER = auto()
    CONTAINS = auto()
    BETWEEN = auto()


def extend_enum(inherited_enum):
    """
    Extended enum annotation method.
    """

    def wrapper(added_enum):
        """
        Wrapper function to extend both enumerations.
        """

        joined = {}
        for item in inherited_enum:
            joined[item.name] = item.value
        for item in added_enum:
            joined[item.name] = item.value
        return Enum(added_enum.__name__, joined)

    return wrapper


@extend_enum(RequestOperations)
class MySQLRequestOperations(Enum):
    """
    MySQL concrete request operations class implementation.
    """

    LIKE = auto()


class FilterRequest(object):
    """
    Filter request class reference.

    Contains the content for the filter request: value
    requested and the request operation that needs.
    """

    def __init__(
        self,
        request_value: Union[object, List[object]],
        request_operation: RequestOperations = RequestOperations.EQUALS,
    ):
        """
        Creates a filter request with specific value and request operation assigned.

        :param request_value: Value or list of values, depending on the parameter number
        :type request_value: Union[object, List[object]]
        :param request_operation: Request operation specified, defaults to RequestOperations.EQUALS
        :type request_operation: RequestOperations, optional
        """

        if not isinstance(request_operation, RequestOperations) and not isinstance(
            request_operation, MySQLRequestOperations
        ):
            raise exceptions.InputParameterException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__init__.__name__
                )
                + "request_operation need to be the enum "
                "type RequestOperations"
            )

        if (
            isinstance(request_value, list)
            and request_operation != RequestOperations.CONTAINS
            and request_operation != RequestOperations.BETWEEN
        ):
            raise exceptions.InputParameterException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__init__.__name__
                )
                + "Request_operation {} does not admit a list as value.".format(
                    str(request_operation)
                )
            )

        self.request_value = request_value
        self.request_operation = request_operation


class SerializeDefaultValues(Enum):
    """
    Serialize default value enumeration class.
    """

    DASH = "-"
    NULL = None


class OrderType(Enum):
    """
    Order type enumeration class.

    For now, there's only two order types:
    ascending and descending.
    """

    ASCENDING = "asc"
    DESCENDING = "desc"


class Pagination(object):
    """
    PES Pagination class provided by DaaS service.

    It contains private attributes in terms of property definition.
    This is a special class for data encapsulation over pages management.
    """

    RESULTS_ATTRIBUTE = "results"
    SERIALIZE_ATTRIBUTE = "serialize"
    DEFAULT_VALUE_ATTRIBUTE = "default_value"
    QUERY_PARAMETERS_ATTRIBUTE = "query"
    TOTAL_ATTRIBUTE = "total_size"
    COUNTS_ATTRIBUTE = "count"
    PAGE_ATTRIBUTE = "page"
    ADDITIONAL_QUERY_PARAMS_ATTRIBUTE = "additional_query_params"

    def __init__(
        self,
        page: int = None,
        page_size: int = None,
        order_by: str = None,
        order_type: OrderType = None,
    ):
        """
        Creates a pagination instance with specific config introduced.

        :param page: Page number (or index in terms of records: 1, 2, 3...)
        :type page: int
        :param page_size: Page size (Number of records per page)
        :type page_size: int
        :param order_by: Order field/property to order by (should be a valid entity attribute)
        :type order_by: str
        :param order_type: Order type enumeration instance (choosing order type)
        :type order_type: OrderType
        """

        if order_type and not isinstance(order_type, OrderType):
            raise exceptions.InputParameterException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__init__.__name__
                )
                + "Order type must be an enumeration Order type class instance"
            )

        if (page and page_size is None) or (page_size and page is None):
            raise exceptions.InputParameterException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__init__.__name__
                )
                + "Page and page size should be provided both (related parameters)"
            )

        if page and page_size:
            try:
                page = int(page)
                page_size = int(page_size)
            except ValueError:
                raise exceptions.InputParameterException(
                    "[{MODULE}][{FUNCTION}]: ".format(
                        MODULE=__name__, FUNCTION=self.__init__.__name__
                    )
                    + "Page or page_size attribute should be an integer"
                )

        self.page = page
        self.page_size = page_size
        self.total_size = None
        self.order_by = order_by
        self.order_type = order_type
        self.additional_query_params = {}

        self.results = list()
        self.default_value = SerializeDefaultValues.NULL.value

    def serialize_value(self, raw_value):
        if isinstance(raw_value, OrderType):
            return raw_value.value

        if raw_value is None:
            return self.default_value
        else:
            return raw_value

    def serialize(self, path):
        """
        JSON representation for this object.

        :return: dict
        """

        self_json = self.__dict__
        response_json = {}
        results = self_json[self.RESULTS_ATTRIBUTE]

        results_list = list()
        for result in results:
            serialize = getattr(result, self.SERIALIZE_ATTRIBUTE, None)

            if callable(serialize):
                results_list.append(serialize())
            else:
                results_list.append(result.__dict__)

        query_params = self.__add_query_parameters(self_json)
        page_url_dict = self.__add_urls_parameters(query_params, path)
        response_json[self.QUERY_PARAMETERS_ATTRIBUTE] = query_params
        response_json[self.RESULTS_ATTRIBUTE] = results_list
        response_json[self.COUNTS_ATTRIBUTE] = len(results_list)
        response_json[self.TOTAL_ATTRIBUTE] = (
            self.total_size if self.total_size is not None else len(results_list)
        )
        response_json.update(**page_url_dict)
        return response_json

    def __add_query_parameters(self, self_json: Dict):
        query_parameters_response = {
            attribute: self.serialize_value(value)
            for attribute, value in self_json.items()
            if attribute
            not in [
                self.DEFAULT_VALUE_ATTRIBUTE,
                self.TOTAL_ATTRIBUTE,
                self.RESULTS_ATTRIBUTE,
                self.ADDITIONAL_QUERY_PARAMS_ATTRIBUTE
            ]
            and value is not None
        }
        # Add extra query parameters
        if hasattr(self, self.ADDITIONAL_QUERY_PARAMS_ATTRIBUTE):
            query_parameters_response.update(getattr(self, self.ADDITIONAL_QUERY_PARAMS_ATTRIBUTE))
        return query_parameters_response

    def __add_urls_parameters(self, query_params, path):

        query_params_string = "&".join(
            {
                f"{attribute}={self.serialize_value(value)}"
                for attribute, value in query_params.items()
                if self.__check_valid_query(attribute, value)
            }
        )

        return_json = {}

        for name in ["self", "first", "last", "prev", "next"]:

            return_json[
                name
            ] = urllib.parse.urljoin(resources.config['HTTP_RESPONSE']['default_domain_url'], path)

            if query_params_string and self.page:

                page_value = self.__get_page_value(name)
                if page_value is None:
                    return_json[name] = page_value
                else:
                    return_json[name] += f"?page={page_value}&{query_params_string}"
        return return_json

    def __check_valid_query(self, attribute, value):
        return (
            attribute
            not in [
                self.DEFAULT_VALUE_ATTRIBUTE,
                self.RESULTS_ATTRIBUTE,
                self.TOTAL_ATTRIBUTE,
                self.PAGE_ATTRIBUTE,
                self.ADDITIONAL_QUERY_PARAMS_ATTRIBUTE
            ]
            and value is not None
        )

    def __get_page_value(self, name):
        page_value = ""
        if self.total_size is None:
            self.total_size = len(self.results)

        if name == "self":
            page_value = self.page
        elif name == "first":
            # Null if we are in the first page
            page_value = 1 if self.page > 1 else None
        elif name == "last":
            # Null if we are in the last page
            max_result =  math.ceil(self.total_size / self.page_size)
            if self.page < max_result:
                page_value = max_result
            else:
                page_value = None
        elif name == "prev":
            # Null if we are in the first page
            page_value = self.page - 1 if self.page > 1 else None
        elif name == "next":
            # Null if we are in the last page
            max_result = math.ceil(self.total_size / self.page_size)
            page_value = self.page + 1 if self.page < max_result else None
        return page_value


class RequestOptions(object):
    """
    DaaS Request options to be selected and specified for
    client operations. This request class is public
    and as every public entity should not have private properties.

    Filters can be associated with primary key restrictions (primary key values),
    standard attributes (non primary key values) or main indexes in case of DynamoDB
    (Global Secondary Indexes). This library will handle all of those options
    and make the best performance queries to obtain those information.

    Every filter should be mapped with a filter request instance indicating the
    filter content: requested value and type operation.

    There is no sense to specify the request database because users would
    obtain database clients to work with those databases, so no specification is
    really needed.

    Pagination and cache flags are going to activate DaaS framework
    cache retrieval methods, internally for Amazon Aurora uses redis exposed
    also with AWS resources library, DynamoDB does not support DAX cache operations
    for now, maybe in a future release might exist.
    """

    def __init__(
        self,
        request_filters: Dict[str, FilterRequest] = None,
        pagination: Pagination = None,
        cache: bool = False,
        cache_multi: bool = False,
        return_values: List[str] = None,
    ):
        """
        Creates a new request options instance with filters and pagination flag.

        Return values parameter is for getting only the specified properties/attributes
        that are in the list provided, if none of them matches with domain fields, would raise
        a request exception with information provided. One thing to the return values is that
        responses from this framework are returned serialized (not with classes
        for both No-SQL and SQL data).

        :param request_filters: Dictionary with field filters, defaults to None
        :type request_filters: Dict[str, FilterRequest], optional

        :param pagination: Pagination instance, defaults to None
        :type pagination: :class: `request_options.Pagination`, optional

        :param cache: Pagination flag, defaults to False
        :type cache: bool, optional

        :param return_values: List with field values to return, defaults to None
        :type return_values: List[str], optional
        """

        if return_values is None:
            return_values = list()

        self.request_filters = self.verify_valid_filters(request_filters)
        self.pagination = pagination
        self.cache = cache
        self.cache_multi = cache_multi
        self.return_values = return_values

    @staticmethod
    def verify_valid_filters(
        request_filters: Dict[str, FilterRequest]
    ) -> Dict[str, FilterRequest]:
        """
        Verify the filter for the user options request.

        :param request_filters: Dictionary with keys as filter name attribute
        along with the filter content
        :type request_filters: Dict[str, FilterRequest]
        :return: filters passing the validation
        :rtype: Dict[str, FilterRequest]
        """

        if not isinstance(request_filters, dict):

            # Filters provided not supported (returning empty ones)
            return dict()

        # Checks specific key-value types and return only the valid ones!
        return {
            value: filter_request
            for value, filter_request in request_filters.items()
            if isinstance(value, str) and isinstance(filter_request, FilterRequest)
        }

    def add_filter(
        self,
        parameter: str,
        value: Union[object, List[object]],
        request_operations: RequestOperations,
    ) -> FilterRequest:
        """
        Add a new filter with value-operation specified.

        :param parameter: key attribute to filter
        :type parameter: str

        :param value: requested value for key attribute
        :type value: str

        :param request_operations: Specific operation for filter
        :type request_operations: RequestOperations

        :return: The filter request object included as filter
        :rtype: FilterRequest
        """

        filter_request = FilterRequest(value, request_operations)

        self.request_filters[parameter] = filter_request

        return filter_request
