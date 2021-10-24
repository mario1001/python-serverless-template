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
    def components(self) -> List[controllers.ProcessingController]:
        return self.__components

    @property
    def results(self) -> List[object]:
        return self.__results

    def __init__(self) -> None:
        """
        Creates a component controller instance.

        When injecting controllers, they are assigned as attributes
        for this instance. Just recollect them in a list for next steps.

        Executes the following controllers injected in time execution with the
        AWS Chalice request introduced.
        """

        self.__components = list()
        self.__results = list()

    def process(self, request: Request) -> None:
        """
        Main procedure for processing the controllers managed by this instance.
        """

        for component in self.components:
            try:
                component.process(request)
                if component.result:
                    self.__results.append(component.result)
            except Exception:
                pass
