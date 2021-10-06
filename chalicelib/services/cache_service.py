# Created in June 17, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice cache service module.

This module englobes the cache interaction (in terms of
service layer). Setting the main functions for cache like
getting some entry by ID fields (ID concatenation or dictionary ones)
or getting a bunch of entries serialized of course.

Cache data should always work with JSONs: List or dictionaries in python.
For now the template does not offer a custom model for that, each project
could have its own declaration and definition.
"""

import ast
import json
from typing import List

import chalicelib.core as core
import chalicelib.domain as domain
import chalicelib.exceptions as exceptions
import chalicelib.logs as logs
import chalicelib.services as services
from aws_resources.cache import CacheRepository


class CacheService(services.Service):
    """
    Cache service class reference.
    """

    @property
    def cache_repository(self) -> CacheRepository:
        return self.__cache_repository

    @cache_repository.setter
    def cache_repository(self, value: CacheRepository):
        if not isinstance(value, CacheRepository):
            value = None

        self.__cache_repository = value

    @core.register("cache")
    def __init__(self) -> None:
        """
        Create a cache service instance with configuration (if so).

        Cache redis is associated with the following default OS environment vars:
        - CACHE_EXPIRATION: Should be a float value (Optional)
        - CACHE_ENDPOINT: Should be a character string value
        - CACHE_PORT: Should be a character string value
        """

        try:
            self.cache_repository = CacheRepository()
        except exceptions.InputParameterException as e:

            logs.system_logger.log(
                "error",
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__init__.__name__
                )
                + "Could not create AWS Resources cache repository: {}".format(
                    str(e)
                ),
            )

            # Service is not active and available somehow (saving none value for methods)
            self.cache_repository = None

    def get_cache_hashmap_values(
        self,
        key: str,
        request_options: domain.RequestOptions = None,
        multi=False,
    ) -> object:
        """
        Try to find some data patterns with cache repository.

        It can be used perfectly by user and for checking items
        with request parameters provided.

        :param key: Key name to retrieve from redis (table name)
        :type key: str

        :param request_options: RequestOptions from query to get the filters from
        :type request_options: RequestOptions, default to None. Optional

        :return: Redis cache values read
        :rtype: object
        """

        # Verify cache service is active to use
        if not self.__verify_cache():
            return

        # Verify what type of cache request is
        # Not allowing here with no available key
        if not key or not isinstance(key, str):
            raise exceptions.ServiceRequestException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__,
                    FUNCTION=self.get_cache_hashmap_values.__name__,
                )
                + "Key must be in string format"
            )
        cache_filters = []
        if request_options:
            cache_filters = self.__get_cache_filters_from_request_options(
                request_options
            )
        value = self.cache_repository.get_hashmap_items(
            key, cache_filters, multi
        )
        logs.system_logger.log(
            "info",
            "[{MODULE}][{FUNCTION}]: Providing {value} from cache repository".format(
                MODULE=__name__,
                FUNCTION=self.get_cache_hashmap_values.__name__,
                value=value,
            ),
        )

        return self.__return_cache_value(value)

    def get_cache_values(self, key: str) -> object:
        """
        Try to find some data patterns with cache repository.

        It can be used perfectly by user and for checking items
        with request parameters provided.

        :param key: Key to set in redis
        :type key: str

        :return: Redis cache values read
        :rtype: object
        """

        # Verify cache service is active to use
        if not self.__verify_cache():
            return

        # Verify what type of cache request is
        # Not allowing here with no available key
        if not key or not isinstance(key, str):
            raise exceptions.ServiceRequestException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.get_cache_values.__name__
                )
                + "Key must be in string format"
            )

        value = self.cache_repository.get_item(key)
        logs.system_logger.log(
            "info",
            "[{MODULE}][{FUNCTION}]: ".format(
                MODULE=__name__, FUNCTION=self.get_cache_values.__name__
            )
            + "Providing {} from cache repository".format(value),
        )
        return self.__return_cache_value(value)

    @staticmethod
    def __get_cache_filters_from_request_options(
        request_options: domain.RequestOptions,
    ) -> List[str]:
        """Private method to build cache filters to retrieve
        values from daas request options

        :param request_options: Requests options from query
        :type request_options: RequestOptions
        :return: List of filters as string
        :rtype: List[str]
        """

        cache_filters: List[str] = []
        # Iterate over request filters to get primary key values
        for _, filter in request_options.request_filters.items():
            # Only get equal filters
            if filter.request_operation == domain.RequestOperations.EQUALS:
                cache_filters.append(str(filter.request_value))
        return cache_filters

    @staticmethod
    def __return_cache_value(value: str) -> object:
        """
        Private method and small algorithm for checking
        retrieved cache values and building the original type.

        :param value: Retrieved cache string value
        :type value: str

        :return: The original raw object introduced in redis
        """

        try:
            # Valid for lists and dictionaries (JSON values)
            return json.loads(value)
        except (TypeError, json.decoder.JSONDecodeError):
            # Checking other conversions
            pass

        try:
            return ast.literal_eval(value)
        except ValueError:
            # Malformed value (sentence to execute or string value)
            pass

        return value

    def __verify_cache(self):
        cache_service = self.cache_repository

        if not cache_service:
            logs.system_logger.log(
                "info",
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.__verify_cache.__name__
                )
                + "Cache service is not"
                "available for this operation (for some reason)",
            )

        return cache_service

    def set_cache_values(
        self, key: str, value: object, expiration: float = None
    ):
        """
        Save some cache information with specific key introduced.

        If cache instance is not ready or not found, this operation
        won't do anything at all.

        :param key: Specific key
        :type key: str
        :param value: Value to save in redis
        :type value: object
        :param expiration: Expiration value
        :type expiration: float
        """

        if not self.__verify_cache():
            return

        if isinstance(value, str):
            return self.cache_repository.save_item(key, value, expiration)

        # Serialize item/items as much as this method can
        if isinstance(value, list):
            value = [self.__serialize_item(item) for item in value]
        else:
            value = self.__serialize_item(value)

        # Ensuring here the element is not a string (first check)
        try:
            value = json.dumps(value)
        except TypeError:
            raise exceptions.ServiceRequestException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.set_cache_values.__name__
                )
                + "Cannot serialize with JSON method"
                "(not even having default one) for this operation"
            )

        return self.cache_repository.save_item(key, value, expiration)

    @staticmethod
    def __serialize_item(value: object) -> dict:
        """
        Private method for serializing an item introduced.

        It would check if has sometype of serialize method
        or would convert into dictionary with the
        default object method.

        :param value: Item to serialize (if not serialized yet)
        :type value: object
        :return: A JSON representation for the object
        :rtype: dict
        """

        if isinstance(value, dict):
            # Object is already serialized (JSON format)
            return value

        serialize = getattr(value, "serialize", None)
        if serialize and callable(serialize):
            # Serialize using the respective method
            value = serialize()

        try:
            # Use the dictionary default method for this object
            value = value.__dict__
        except AttributeError:
            pass

        try:
            # Try to convert this iterable into list (if so)
            value = list(value)
        except TypeError:
            pass

        # Could not serialize this value, return it the way it is (cache method would handle)
        return value

    def set_cache_hashmap_values(self, cache_data_hashmap):
        """
        Save some cache information with specific key introduced.

        If cache instance is not ready or not found, this operation
        won't do anything at all.

        :param key: Specific key
        :type key: str
        :param value: Value to save in redis
        :type value: object
        """

        if not self.__verify_cache():
            return

        if isinstance(cache_data_hashmap, dict):
            self.cache_repository.save_hash_items(cache_data_hashmap)
