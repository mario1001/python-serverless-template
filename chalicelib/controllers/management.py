# Created in October 24, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless microservice template management module.

Suggest different ways for bean management (this includes components as well).
Main role for this module is just the definition of the component processing controller
for the application context.

Management processes should mantain the performance at all cost along with
the software design pattern composition.
"""

from typing import List

import chalicelib.controllers as controllers
import chalicelib.core as core
import chalicelib.logs as logs
from chalice.app import Request


class ComponentManagementController(controllers.ProcessingController):
    """
    Component management controller class reference.

    Designed for component management in the end. Provides
    different way for processing controllers in the application context.

    Using the composite design pattern on other controllers. It's just
    a controller for processing assigned controllers from context requests.
    """

    @property
    def bean_controller(
        self,
    ) -> controllers.translator.BeanController:
        return self.__bean_controller

    @bean_controller.setter
    def bean_controller(self, value):
        self.__bean_controller = value

    @property
    def components(self) -> List[controllers.ProcessingController]:
        return self.__components

    @core.register("manager")
    @core.inject(ref=controllers.translator.BeanController)
    def __init__(self) -> None:
        """
        Creates a component controller instance.

        When injecting controllers, they are assigned as attributes
        for this instance. Just recollect them in a list for next steps.

        Executes the following controllers injected in time execution with the
        AWS Chalice request introduced.
        """

        super().__init__()

        self.__components = list()
        for component in vars(self).values():
            self.components.append(component)

        self.result = list()

    def process(self, request: Request) -> None:
        """
        Main procedure for processing the controllers managed by this instance.
        """

        for component in self.components:
            if not isinstance(component, controllers.ProcessingController):
                continue

            try:
                component.process(request)
                if component.result:
                    self.result.append(component.result)
            except Exception as exception:
                logs.system_logger.log(
                    "error",
                    "[{MODULE}][{FUNCTION}]: ".format(
                        MODULE=__name__, FUNCTION=self.process.__name__
                    )
                    + "Specific exception when processing component "
                    + f"{component.__class__.__name__}: {exception}",
                )
