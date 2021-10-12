# Created in October 9, 2021 by Mario Benito.
#
# Free Software design purposes at any version of this repository.

"""
Python Serverless microservice template translator module.

Defines a translator controller for creating models in time execution.
"""

import inspect
from typing import Dict, List

import chalicelib.core as core
import chalicelib.controllers as controllers

from pathlib import Path

from chalice.app import Request


class BeanController(controllers.Controller):
    """
    Bean controller class reference.

    This controller should be used for translation between
    certain data (AWS Chalice requests into beans).
    """

    ROOT_PACKAGES = ["dto", "domain"]
    DOUBLE_UNDERSCORES = "__"

    @property
    def path_parameter_controller(
        self,
    ) -> controllers.validation.PathParameterController:
        return self.__path_parameter_controller

    @path_parameter_controller.setter
    def path_parameter_controller(self, value):
        self.__path_parameter_controller = value

    @property
    def query_parameter_controller(
        self,
    ) -> controllers.validation.QueryParameterController:
        return self.__query_parameter_controller

    @query_parameter_controller.setter
    def query_parameter_controller(self, value):
        self.__query_parameter_controller = value

    @property
    def body_controller(
        self,
    ) -> controllers.validation.BodyController:
        return self.__body_controller

    @body_controller.setter
    def body_controller(self, value):
        self.__body_controller = value

    @core.inject(ref=controllers.validation.PathParameterController)
    @core.inject(ref=controllers.validation.QueryParameterController)
    @core.inject(ref=controllers.validation.BodyController)
    def __init__(self) -> None:
        """
        Create a new translator bean instance.

        Intended for only one request per execution, always resetting
        the memory for next steps (this should be taken for granted).
        """

        super().__init__()
        self.__log_parameter_controllers(
            [self.path_parameter_controller, self.query_parameter_controller]
        )

    @core.logger
    def __log_parameter_controllers(
        self, controllers: List[controllers.validation.ParameterController]
    ) -> None:
        """
        Private method for logging the parameters in controllers injected.
        """

    @core.logger
    def create_bean(self, request: Request):
        """
        Create a bean with AWS Chalice request.

        Firstly scans every available resource as model
        (DTO/domain classes existing in the template packages).

        :param request: AWS Chalice request mapped
        :type request: chalice.app.Request
        """

        self.path_parameter_controller.process(request=request)
        self.query_parameter_controller.process(request=request)
        self.body_controller.process(request=request)

        path_parameters = self.path_parameter_controller.parameters
        query_parameters = self.query_parameter_controller.parameters
        global_parameters = {**path_parameters, **query_parameters}

        for model in self.ROOT_PACKAGES:
            class_ = self.inspect_model(
                domain_package=Path(__file__).parent / model,
                parameters={**path_parameters, **query_parameters},
            )

            if class_:
                break

        self.reset()
        return class_(**global_parameters)

    @classmethod
    def inspect_model(
        cls,
        model_package: str,
        table_name: str = None,
        parameters: Dict[str, str] = dict(),
    ) -> type:
        """
        Main method for getting domain model classes (or other types if so)
        that make references to the table name introduced as parameter.

        Uses inspecting features in some configured module. Also checks
        for submodules inside this one.

        Raises an exception when searches don't provide any located class.

        :param table_name: Table name in domain package
        :type table_name: str
        :return: Custom class instance (with inheritance or not)
        :rtype: type
        """

        model_package_module = cls.import_package(model_package)

        """
        for module in dir(model_package_module):
            if not module.startswith(DOUBLE_UNDERSCORES):
                class_ = getattr(model_package_module, module)
                if (
                    inspect.isclass(class_)
                    and hasattr(class_, class_property)
                    and getattr(class_, class_property) == table_name
                ):
                    return class_
        """

        # Should be managed externally
        raise Exception()

    @staticmethod
    def import_package(name):
        """
        Loads dynamically some specific package/subpackage.

        :param name: specific path for package
        :type name: str

        :return: object (could be module or class in our case)
        """

        components = name.split(".")
        mod = __import__(components[0])
        for comp in components[1:]:
            mod = getattr(mod, comp)
        return mod
