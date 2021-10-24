# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless context module in core functionalities.

What a context is in this template (or what does it mean)? Core module
provides a project/workspace context (based in the Spring framework context but
with a serverless orientation).

Provides and manages a serverless context with this application.
This feature is integrated as a core concept for instance dependency injection
for different components of this template.

By components, we mean the following ones: controllers, services and repositories.
"""

from __future__ import annotations
from abc import ABCMeta

from typing import Dict, List, Tuple

import chalicelib.controllers as controllers
import chalicelib.core as core
import chalicelib.exceptions as exceptions
import chalicelib.logs as logs
from aws_resources.exceptions import http_exceptions
from chalice.app import Request


class ApplicationContext(metaclass=core.singleton.SingletonMeta):
    """
    Application context class reference.

    Being influenced by Spring framework with @Autowired
    annotation for injecting the beans/instances
    for our serverless application.

    It does know the policies for bean control but
    it's not designed for user purposes (unlike annotations),
    extending from this class would mean some changes applied to the
    original, keep in mind the documentation here designed for
    saving beans along with the core.

    There's only one instance when running a chalice application, following
    the singleton pattern also for context, makes metadata class registries.

    Does provide a property for getting the beans working with (this one
    it's pretty different from Spring configuration, allowing here some
    fresh freedom).
    """

    @property
    def invocated_function(self):
        return self.__invocated_function

    @invocated_function.setter
    def invocated_function(self, value):
        self.__invocated_function = value

    @property
    def requests(
        self,
    ) -> Dict[Tuple[function, Request], List[controllers.Controller]]:
        return self.__requests

    @requests.setter
    def request(self, value: Request):
        """Property for populating a AWS Chalice request.

        Not only saving the request, also active the core configuration system.
        Just setting up controllers for defining the beans within that saved request.

        :param value: AWS Chalice request to be stored
        :type value: chalice.app.Request
        """

        self.__requests[value] = self.inject_components(value)

    def inject_components(self, request: Request) -> List[object]:
        """
        Inject the component management controller instance
        for processing a request.

        :param value: AWS Chalice request causing the component injection
        :type value: chalice.app.Request

        :return: List of results obtained from management controller
        :rtype: List[object]
        """

        return list()

    @core.classproperty
    def application_context(cls) -> ApplicationContext:

        context = None
        if not hasattr(cls, f"{context=}".split("=")[0]):
            cls.context = None

        return cls.context

    @property
    def injection_class(self):
        return self.__injection_class

    # Active beans living and registered in context
    # There's a busy mechanism for searches with specific injection
    # If key is provided, the instance representing that entry would be returned

    @property
    def active_beans(self) -> Dict[str, object]:
        return self.__active_beans

    @active_beans.setter
    def active_beans(self, value):
        self.__active_beans = value

    @property
    def registry(self) -> dict:
        return self.__registry

    @registry.setter
    def registry(self, value):
        self.__registry = value

    @property
    def registering_type(self):
        return self.__registering_type

    @registering_type.setter
    def registering_type(self, value):
        self.__registering_type = value

    def __init__(self, invocated_function) -> None:
        self.invocated_function = invocated_function
        self.__requests = dict()

        self.registry = {}

        # Registering type for every custom class developed
        # Custom core classes could be created this way and registering them
        # into this context instance.

        class RegisteringType(type):
            def __init__(cls, name, bases, attrs):
                for key, val in attrs.items():
                    properties = getattr(val, "register", None)
                    if properties is not None:
                        self.registry["%s.%s" % (name, key)] = properties

        class Component(ABCMeta, RegisteringType):
            """
            Base Abstract class with context beans implementation.

            Every new layer feature to inject should
            have this metaclass (as declaration).
            """

        self.__injection_class = Component
        self.active_beans = dict()

    def __call__(self, *args, **kwargs):

        # Request Service initialization (initial load for next operations before handler execution)
        # If other resources need to be initialized before business logic goes, here they should be

        # Core context would rise up when running the application
        ApplicationContext.context = self

        # Run specific handler function (for validation or check filters whatever)
        return self.invocated_function(*args, **kwargs)

    def __create_bean(self, reference, values, injection_name, key):
        try:
            if isinstance(values, dict):
                bean = reference(**values)
            else:
                bean = reference(*values)

            logs.system_logger.log(
                "info",
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.request_instance.__name__
                )
                + "Creating bean of type {reference}: {bean}".format(
                    reference=reference.__name__, bean=str(bean)
                ),
            )
        except http_exceptions.BadRequestException as e:
            raise e
        except Exception as e:

            # Incorrect constructor bean, raise injection exception
            raise exceptions.DependencyInjectionException(
                "[{MODULE}][{FUNCTION}]: ".format(
                    MODULE=__name__, FUNCTION=self.request_instance.__name__
                )
                + "Occurred some error when creating {type}: {error}".format(
                    type=reference.__name__, error=str(e)
                ),
            )

        self.active_beans[injection_name + "&" + "&".join(key)] = bean
        return bean

    def request_instance(self, reference: object, values: list) -> object:
        """
        Request method called when injecting wrapper is actived
        within the context.

        :param reference: Type to inject (could be a class
        type or module, depends on the needs)
        :type reference: object

        :param values: Arguments passed in inject decorator (in terms of a list)
        :type values: list

        :return: Some instance of IoC container
        :rtype: object
        """

        # Here goes the policy for our IoC container:
        #
        # Form following keys:
        #
        # - Class_name.arg1&arg2&... (for arg in key)
        #
        # Check active beans firstly (bean could not be registered)
        # and search the key registered, just give instances depending on the
        # availability, it key is unregistered, create the new bean

        injection_name = values.pop(0)

        for entry, key in self.registry.items():
            if entry.split(".")[0] == injection_name:
                # Type class found in registry

                key_value = injection_name
                if key[0]:
                    key_value = (
                        key_value + "&" + "&".join(key[0]) + "&"
                        if key[1]
                        else "" + "&".join([value for value in key[1].values()])
                    )
                elif key[1]:
                    key_value = (
                        key_value
                        + "&"
                        + "&".join([value for value in key[1].values()])
                    )

                bean = self.active_beans.get(key_value, None)

                if not bean:
                    # Just create a new one and save it as active

                    bean = self.__create_bean(
                        reference, values, injection_name, key_value
                    )

                return bean

        raise exceptions.DependencyInjectionException(
            "[{MODULE}][{FUNCTION}]: ".format(
                MODULE=__name__, FUNCTION=self.request_instance.__name__
            )
            + "The injection type was not found in registry",
        )
