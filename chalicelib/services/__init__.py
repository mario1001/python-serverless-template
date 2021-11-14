# Created in June 14, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless template microservice service main module.

Defines the different functions on service layer. Also
here stays the interface for services (every service should
inherit from that class to be injected).

A service must contain business logic operatives (which can differ
from projects) but should remain as a service component definition
with its interface (just as Spring does for example).
"""

from abc import ABC

from chalice.app import Request
import chalicelib.core as core
import chalicelib.controllers as controllers


class Service(
    ABC, metaclass=core.ApplicationContext.application_context.injection_class
):
    """
    Abstract service interface reference.

    Using core processing requests with controllers, you would have the data
    in the request (specifically in the bean controller result with the model object).

    You can always pass the attributes from handler layer (without forming any model) or you could
    also use this service interface for making the process here in the service layer.
    """

    @property
    def bean_controller(
        self,
    ) -> controllers.translator.BeanController:
        return self.__bean_controller

    @bean_controller.setter
    def bean_controller(self, value):
        self.__bean_controller = value

    @core.register("default")
    @core.inject(ref=controllers.translator.BeanController)
    def __init__(self) -> None:
        """
        Creates a new service instance with bean controller injected.

        Beans could be saved within application context, as well as you
        also have the chance for constructing model with this injected service.

        When creating services with different bean controller classes should never
        call this constructor because it's injecting a simple one (or if
        you don't mind, at your choice).
        """

        super().__init__()

    def create_bean(self, request: Request) -> object:
        return self.bean_controller.create_bean(request)
